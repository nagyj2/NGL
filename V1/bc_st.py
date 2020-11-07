# ngl bytecode symbol table

# The symbol table is represented by a dictionary.
# The symbols are indexed into the dictionary by the identifier name

import re
from bc_sc import INT, FLOAT, BOOL, STRING, NULL, GOARROW1, GOARROW2, mark, init as sc_init
from bc_sc import *

class Collection:
    def __init__(self, edit, inputs):
        self.edit = edit
        # True = List; False = Array
        self.collect = []
        for elem in inputs: #Assumes input is
            self.collect.append(elem)

    def addElem(self,value):
        c_value = self.__conv(value)
        if c_value != None:
            self.collect.append(c_value)

    def __getitem__(self,index):
        try: return self.collect[index]
        except IndexError: return None

    def __setitem__(self,index,value):
        if self.edit:
            if index >= len(self.collect): mark('assignment is out of range')
            else: self.collect[index] = value
        else: mark('arrays are non-mofifiable')

    def __len__(self):
        return len(self.collect)

    def __iter__(self):
        self.i = 0
        return self

    def __next__(self):
        if self.i > len(self.collect):
            raise StopIteration
        else:
            result = self.collect[self.i]
            self.i+=1
            return result

    def __conv(self,elem):
        if len(self.collect)==0: return
        elif type(self.collect[0]) == int:
            return int(elem)
        elif type(self.collect[0]) == float:
            return float(elem)
        elif type(self.collect[0]) == str:
            return str(elem)
        elif type(self.collect[0]) == bool:
            return bool(elem)
        return

    def __add__(self, other):
        if self == other: # Adding to self makes an endless loop
            other = Collection(other.edit,other.collect)
        if self.edit:
            if type(other) != Collection: # Adding collections
                n_other = self.__conv(other)
                if n_other != None: self.collect.append(n_other)
                else: mark('failed conversion')
            else: # Adding individual element and collection
                for i,elem in enumerate(other.collect):
                    n_elem = self.__conv(elem)
                    if n_elem != None: self.collect.append(n_elem)
                    else: mark('failed conversion')
        else: mark('arrays are non-mofifiable')
        return self

    def __radd__(self, other):
        return self + other

    def __sub__(self, other):
        if self == other: # Adding to self makes an endless loop
            other = Collection(other.edit,other.collect)
        if self.edit:
            if type(other) != Collection:
                n_other = self.__conv(other)
                if n_other != None:
                    try: self.collect.remove(n_other)
                    except ValueError: mark('element not in collection')
                else: mark('failed conversion')
            else:
                for i,elem in enumerate(other.collect):
                    n_elem = self.__conv(elem)
                    if n_elem != None:
                        try: self.collect.remove(n_elem)
                        except ValueError: mark('element not in collection')
                    else: mark('failed conversion')
        else: mark('arrays are non-mofifiable')
        return self

    def __rsub__(self, other):
        return self - other

    def __mul__(self, other):
        return self

    def __div__(self, other):
        return self

    def __mod__(self, other):
        return self

    def __rmul__(self, other):
        return self

    def __int__(self):
        mark('collection cannot be cast to int')
        return self
    def __float__(self):
        mark('collection cannot be cast to float')
        return self
    def __bool__(self):
        mark('collection cannot be cast to bool')
        return self
    def __str__(self):
        toRet = '['
        if len(self.collect)>=1:
            toRet += str(self.collect[0])
            for elem in self.collect[1:]:
                if type(elem) == Collection: mark('nested collections are illegal'); break
                toRet += ',' + str(elem)
        toRet += ']'
        return toRet

def init(src):
    global symTab, jmpTab
    symTab = {} # {'_temp': (0,INT)} # For variables. Entries are tuples with (value,type)
    jmpTab = {'<-': [], '<=': [], '->': [], '=>': []} # For jump statements

    re_label = ('^[_]?[A-Za-z0-9]+[A-Za-z0-9_]*:') # Labels
    re_retarrow1 = ('^<-') # Return Arrow 1
    re_retarrow2 = ('^<=') # Return Arrow 2
    re_goarrow1 = ('^->') # Go Arrow 1
    re_goarrow2 = ('^=>') # Go Arrow 2
    index = 0
    for i,line in enumerate(src.splitlines()):
        # TODO: line and pos should be saved (to allow multiple statements on one line without jumps getting confused)
        line = line.lstrip()
        noA1=True

        isRetArrow1 = re.compile(re_retarrow1 + '\s*').match(line)
        if isRetArrow1:
            # <- match
            line = line[len(isRetArrow1.group()):]
            newJump('<-',i)
        else:
            isGoArrow1 = re.compile(re_goarrow1 + '\s*').match(line)
            if isGoArrow1:
                # -> match
                line = line[len(isGoArrow1.group()):]
                newJump('->',i)

        isRetArrow2 = re.compile(re_retarrow2 + '\s*').match(line)
        if isRetArrow2:
            # <= match
            line = line[len(isRetArrow2.group()):]
            newJump('<=',i)
        else:
            isGoArrow2 = re.compile(re_goarrow2 + '\s*').match(line)
            if isGoArrow2:
                # => match
                line = line[len(isGoArrow2.group()):]
                newJump('=>',i)

        isLabel = re.compile(re_label).match(line)
        if isLabel:
            # label too
            label = isLabel.group()[:-1]
            newJump(label,i)

        index += len(line) # TODO: Doesnt this result in index not getting properly updated?

def printSymTab():
    for i, (n, v) in enumerate(symTab.items()):
        print(n, ":", v)
    print()

def printJmpTab():
    for i, (n, v) in enumerate(jmpTab.items()):
        print(n, ":", v)
    print()

def newDecl(name : str, typ, value = None):
    if name in symTab and typ != symTab[name][1]:
        mark("variable type change")
    else:
        symTab[name] = (value if value != None else None, typ)

def delDecl(name : str):
    if name not in symTab:
        return
        mark("non-existant variable")
    del symTab[name]

def assignDecl(name : str, typ, value, index = None):
    if not name in symTab:
        mark("no variable")
    else:
        old_value, old_typ = symTab[name]

        if old_typ != typ: mark('type mismatch')
        else:
            if index == None or type(old_value) != Collection: symTab[name] = (value, old_typ)
            elif old_value.edit: old_value[index] = value
            else: mark('invalid assignment')

def newJump(name : str, line):
    if name in jmpTab:
        if name in {'<-', '->', '<=', '=>'}:
            jmpTab[name].append(line)
        else:
            mark("multiple jump definitions")
    else:
        jmpTab[name] = line

def findDecl(name : str):
    if name in symTab:
        value,typ = symTab[name]
        return (value,typ)
    mark('undefined variable identifier: ' + name)
    return (0,INT) # TODO: Should return 'null' equivalent

def findJump(name : str, currline=None, back=0):
    if name in jmpTab:
        if name in {'<-', '<='}:
            array = jmpTab[name]
            lastGreater = False
            for i in range(len(array)):
                if (not lastGreater and array[i]>currline):
                    lastGreater=True
                elif (lastGreater and array[i]>currline):
                    try: return array[i-1+back]
                    except IndexError: mark('1. non-existant destination'); return array[-1]
            try: return array[-1+back]
            except IndexError: mark('2. non-existant destination'); return array[-1]
        elif name in {'->', '=>'}:
            array = jmpTab[name]
            for i in range(len(array)):
                if (array[i]>currline):
                    return array[i-1-back]
            try: return array[-1-back]
            except IndexError:
                mark('3. non-existant destination')
                print(name,array,1+back)
                return array[-1]
        else:
            return jmpTab[name]

    mark('undefined jump identifier ' + name)
    return currline

if __name__ == '__main__':
    sc_init('')
    init()

    newDecl('var1',4)
    newDecl('var2',6.3)
    newDecl('bess',True)
    newDecl('var3',"hi")

    printSymTab()
