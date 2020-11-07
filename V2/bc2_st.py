# NGL Bytecode 2.0 Symbol Table
from copy import deepcopy
import bc2_sc as SC
from bc2_sc import INT, FLOAT, BOOL, STRING, NULL, ARRAY, LIST, GOARROW1, GOARROW2, RETARROW1, RETARROW2, RETURN, PLUS, MINUS, MULT, DIV, MOD, EXP, AND, OR, EQ, NE, LT, GT, mark

TYPES = {INT, FLOAT, BOOL, STRING, NULL}
ARROWS = {GOARROW1, GOARROW2, RETARROW1, RETARROW2}

class Variable:
    @staticmethod
    def NULL():
        return Variable(NULL,None,True)

    def __init__(self, typ : int, value, const : bool = False):
        if typ not in TYPES:
            mark('invalid variable type')
            self.typ, self.value, self.const = NULL, None, True
        elif value != None and typ == NULL or value == None and typ != NULL:
            mark('null variable has only one value')
            self.typ, self.value, self.const = NULL, None, True
        elif typ == NULL and const == False:
            mark('null must be constant')
            self.typ, self.value, self.const = NULL, None, True
        else:
            self.typ, self.const = typ, const
            self.value = self.__conv(value)

    def __getitem__(self, index : int):
        if type(index) == Variable:
            if index.typ != INT:
                mark('non-integer index')
                return Variable(INT,0)
            index = index.value
        if self.typ != STRING:
            mark('variable cannot be indexed'); return Variable(INT,0)
        elif index >= len(self.value):
            mark('invalid index'); return Variable(INT,0)
        return Variable(STRING,self.value[index])

    def __conv(self,elem):
        if self.typ == INT:
            return int(elem)
        elif self.typ == FLOAT:
            return float(elem)
        elif self.typ == STRING:
            return str(elem)
        elif self.typ == BOOL:
            return bool(elem)
        elif self.typ == NULL:
            return None
        mark('invalid conversion')

    def __int__(self):
        return int(self.value)
    def __float__(self):
        return float(self.value)
    def __bool__(self):
        return bool(self.value)
    def __str__(self):
        return str(self.value)
    def __invert__(self):
        return not(self.value)

    def __add__(self,other):
        if type(other) == Variable:
            if other.typ == self.typ or other.typ == {INT,FLOAT} and self.typ in {INT,FLOAT}:
                return self.__resolve(other,PLUS)
            else: raise Exception('not implemented for types')
        else: # Collection
            if other.typ != self.typ:   mark('variable and collection mismatch')
            else:                       other.collect.append(self)
            return other
    def __radd__(self,other):
        return self + other
    def __sub__(self,other):
        if type(other) == Variable:
            if other.typ == self.typ or other.typ == {INT,FLOAT} and self.typ in {INT,FLOAT}:
                return self.__resolve(other,MINUS)
            else: raise Exception('not implemented for types')
        else: # Collection
            mark('cannot subtract collection from variable')
            return other
    def __rsub__(self,other):
        if type(other) == Variable:
            return -self + other
        else: # Collection
            if other.typ != self.typ:
                mark('variable and collection mismatch')
            else:
                try: other.collect.remove(self)
                except ValueError: mark('variable not in collection (check me)')
                return other
    def __mul__(self,other):
        if type(other) == Variable:
            if other.typ == self.typ or other.typ == {INT,FLOAT} and self.typ in {INT,FLOAT}:
                return self.__resolve(other,MULT)
            else: raise Exception('not implemented for types')
        else: # Collection
            raise Exception('not implemented')
    def __rmul__(self,other):
        return self * other
    def __truediv__(self,other):
        if type(other) == Variable:
            if other.typ == self.typ or other.typ == {INT,FLOAT} and self.typ in {INT,FLOAT}:
                return self.__resolve(other,DIV)
            else: raise Exception('not implemented for types')
        else: # Collection
            raise Exception('not implemented')
    def __rtruediv__(self,other):
        if type(other) == Variable:
            return self.__resolve(self,'inv') * other
        else: # Collection
            raise Exception('not implemented')
    def __mod__(self,other):
        if type(other) == Variable:
            if other.typ == self.typ or other.typ == {INT,FLOAT} and self.typ in {INT,FLOAT}:
                return self.__resolve(other,MOD)
            else: raise Exception('not implemented for types')
        else: # Collection
            raise Exception('not implemented')
    def __pow__(self,other):
        if type(other) == Variable:
            if other.typ == self.typ or other.typ == {INT,FLOAT} and self.typ in {INT,FLOAT}:
                return self.__resolve(other,EXP)
            else: raise Exception('not implemented for types')
        else: # Collection
            raise Exception('not implemented')
    def __lt__(self,other):
        if type(other) == Variable:
            if other.typ == self.typ or other.typ == {INT,FLOAT} and self.typ in {INT,FLOAT}:
                return self.__resolve(other,LT)
            else: raise Exception('not implemented for types')
        else: # Collection
            raise Exception('not implemented')
    def __gt__(self,other):
        if type(other) == Variable:
            if other.typ == self.typ or other.typ == {INT,FLOAT} and self.typ in {INT,FLOAT}:
                return self.__resolve(other,GT)
            else: raise Exception('not implemented for types')
        else: # Collection
            raise Exception('not implemented')
    def __eq__(self,other):
        if type(other) == Variable:
            return self.__resolve(other,EQ)
        else: # Collection
            return Variable(BOOL,False)
            raise Exception('not implemented')
    def __ne__(self,other):
        if type(other) == Variable:
            return self.__resolve(other,NE)
        else: # Collection
            return Variable(BOOL,True)
            raise Exception('not implemented')
    def __and__(self,other):
        if type(other) == Variable:
            if other.typ == self.typ == BOOL:
                return self.__resolve(other,AND)
            else: raise Exception('not implemented for types')
        else: # Collection
            raise Exception('not implemented')
    def __or__(self,other):
        if type(other) == Variable:
            if other.typ == self.typ == BOOL:
                return self.__resolve(other,OR)
            else: raise Exception('not implemented for types')
        else: # Collection
            raise Exception('not implemented')
    def __neg__(self):
        return self.__resolve(self,'-')

    def __resolve(self,other, op):
        if op == PLUS: val = self.value + other.value
        elif op == MINUS: val = self.value - other.value
        elif op == MULT: val = self.value * other.value
        elif op == DIV: val = self.value / other.value
        elif op == MOD: val = self.value % other.value
        elif op == EXP: val = self.value ** other.value
        elif op == AND: val = self.value and other.value
        elif op == OR: val = self.value or other.value
        elif op == EQ: val = self.value == other.value
        elif op == NE: val = self.value != other.value
        elif op == LT: val = self.value < other.value
        elif op == GT: val = self.value > other.value

        elif op == '-': val = - self.value
        elif op == 'inv': val = 1 / self.value
        else: mark('unknown operator')

        if type(val) == int: typ = INT
        elif type(val) == float: typ = FLOAT
        elif type(val) == str: typ = STRING
        elif type(val) == bool: typ = BOOL
        else: mark('unknown type')

        return Variable(typ,val)

class Collection:
    # const = True -> Array
    # const = False -> List
    def __init__(self,typ : int, inputs : list, const):
        self.collect,self._i = [],0
        if typ not in TYPES - {NULL}:
            # NOTE: NULL collections are illegal
            mark('invalid variable type')
            self.typ, self.const = NULL, True
        elif type(inputs) != list:
            mark('collection requires list input')
            self.typ, self.const = NULL, True
        else:

            if type(const) == bool: self.const = const
            elif const == ARRAY: self.const = True
            else: self.const = False # LIST is entered
            self.typ = typ

            for elem in inputs:
                if type(elem) != Variable or elem.typ != self.typ:
                    mark('collection element type mismatch')
                else:
                    # elem.const = self.const
                    self.collect.append(elem)

    def __conv(self,elem):
        if self.typ == INT:
            return int(elem)
        elif self.typ == FLOAT:
            return float(elem)
        elif self.typ == STRING:
            return str(elem)
        elif self.typ == BOOL:
            return bool(elem)
        mark('invalid conversion')

    def __getitem__(self, index):
        if type(index) == Variable:
            if index.typ != INT:
                mark('non-integer index')
                return Variable(INT,0)
            index = index.value
        if index >= len(self.collect):
            mark('invalid index'); return 0
        return self.collect[index]

    def __setitem__(self, index : int, value):
        if self.const:
            mark('arrays are non-mofifiable')
        else:
            if index >= len(self.collect): mark('assignment is out of range')
            else: self.collect[index].value = value

    def __len__(self):
        return len(self.collect)

    def __iter__(self):
        self._i = 0
        return self

    def __next__(self):
        if self._i >= len(self.collect):
            raise StopIteration
        else:
            result = self.collect[self._i]
            self._i += 1
            return result

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
            toRet += str(self.collect[0].value)
            for elem in self.collect[1:]:
                toRet += ',' + str(elem.value)
        toRet += ']'
        return toRet

    def __add__(self,other):
        if type(other) == Variable:
            if self.const: mark('cannot modify array'); return self
            if self.typ != other.typ:   mark('variable and collection mismatch')
            else:                       self.collect.append(other)
            return self
        else: # Collection
            for elem in other:
                if self.typ != elem.typ:    mark('variable and collection mismatch')
                else:                       self.collect.append(elem)
            return self

    def __sub__(self,other):
        if type(other) == Variable:
            if self.const: mark('cannot modify array'); return self
            if self.typ != other.typ:   mark('variable and collection mismatch')
            try:                self.collect.remove(other)
            except ValueError:  mark('variable not in collection [check me]')
            return self
        else: # Collection
            for elem in other:
                if self.typ != elem.typ:    mark('variable and collection mismatch')
                else:                       self.collect.remove(elem)
            return self

def init(src : str):
    global symTab, jmpTab
    # For variables. Must be put into Variable objects before being entered
    symTab = {}
    # For jump statements NOTE: when adding arrows, add the OPPOSITE to what you find
    # i.e. GOARROWs enter a RETARROW location and vice-versa
    jmpTab = {GOARROW1: [], GOARROW2: [], RETARROW1: [], RETARROW2: [], RETURN: 0}

def printSymTab():
    for i, (n, v) in enumerate(symTab.items()):
        print(n, ":", v)
    print()

def printJmpTab():
    for i, (n, v) in enumerate(jmpTab.items()):
        if n == GOARROW1: n = '<-'
        elif n == GOARROW2: n = '<='
        elif n == RETARROW1: n = '->'
        elif n == RETARROW2: n = '=>'
        elif n == RETURN: n = '_r'
        print(n, ":", v)
    print()

def newDecl(name : str, var : Variable = Variable.NULL()):
    if type(var) not in (Variable, Collection):
        mark('variable object must be made first')
    elif name in symTab and var.typ != symTab[name].typ:
        mark("variable type change")
    else:
        symTab[name] = var

def delDecl(name : str):
    if name not in symTab: mark("non-existant variable")
    else: del symTab[name]

def assignDecl(name : str, var : Variable = Variable.NULL(), index : int = -1):
    if not name in symTab:
        mark("no variable")
    else:
        old_var = symTab[name]

        if old_var.typ != var.typ or type(var) != type(old_var): mark('type mismatch')
        else:
            if old_var.const:
                # FIX: const array vs const contents vs non-const contents?
                if type(old_var) == Variable: mark('constant cannot be changed')
                else: mark('arrays cannot be modified')
            elif type(old_var) == Variable:
                symTab[name] = var
            elif type(old_var) == Collection:
                if type(var) == Variable:
                    if index < len(old_var): old_var[index] = var
                    else: mark('index out of bounds')
                else: # Collection
                    symTab[name] = var
            else: mark('invalid assignment')

def findDecl(name):
    if name in symTab:
        return symTab[name]
    mark('undefined variable identifier: ' + name)
    return Variable.NULL()

def newJump(name, line):
    if name in jmpTab:
        # NOTE: b/c of how the preprocessor is 1 pass, arrows are entered in order
        if name in ARROWS:
            if line not in jmpTab[name]:    jmpTab[name].append(line)
        elif name == RETURN:                jmpTab[name] = line
        else:                               mark("multiple jump definitions")
    else:                                   jmpTab[name] = line

def findJump(name, currline : int, back : int = 0):
    if name in jmpTab:
        if name in {GOARROW1, GOARROW2}:
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
        elif name in {RETARROW1, RETARROW2}:
            array = jmpTab[name]
            for i in range(len(array)):
                if (array[i]>currline):
                    return array[i-1-back]
            mark('no matching return arrow')
            return currline
        else:
            return jmpTab[name]
    mark('undefined jump identifier ' + name)
    return currline

def pollJump(name):
    if name in jmpTab:
        return jmpTab[name]
    else:
        mark('undefined jump identifier '+name)
        return SC.line

def save():
    global symTab, jmpTab
    symTabCopy = deepcopy(symTab)
    jmpTabCopy = deepcopy(jmpTab)
    return (symTabCopy, jmpTabCopy)

def load(symTabCopy, jmpTabCopy):
    global symTab, jmpTab
    symTab = symTabCopy
    jmpTab = jmpTabCopy

if __name__ == '__main__':
    src='''
var i::int 5;
'''

    SC.init(src)
    init(src)

    newDecl('int', Variable(INT,1))
    newDecl('intC', Variable(INT,2,True))
    newDecl('float', Variable(FLOAT,1))
    newDecl('floatC', Variable(FLOAT,2.0,True))
    newDecl('string', Variable(STRING,"a"))
    newDecl('stringC', Variable(STRING,"A",True))
    newDecl('bool', Variable(BOOL,False))
    newDecl('boolC', Variable(BOOL,True,True))

    assignDecl('int',Variable(INT,10))
    assignDecl('float',Variable(FLOAT,10))
    assignDecl('string',Variable(STRING,'10'))
    assignDecl('bool',Variable(BOOL,True))

    vars = [Variable(INT,2), Variable(INT,4), Variable(INT,6),
            Variable(INT,8), Variable(INT,10)]

    newDecl('list',Collection(INT,vars,True))
    newDecl('listC',Collection(INT,vars,False))

    delDecl('int')
    delDecl('intC')
    delDecl('list')
    # delDecl('listg')

    # assignDecl('intC',Variable(INT,10))
    # assignDecl('floatC',Variable(FLOAT,10))
    # assignDecl('stringC',Variable(STRING,'10'))
    # assignDecl('boolC',Variable(BOOL,False))

    # print(findDecl('boolC'))
    # print(findDecl('float'))
    # print(findDecl('listC'))

    # printSymTab()

    # newJump('start',0)
    # newJump('end',5)
    # newJump(GOARROW1,3)
    # newJump(GOARROW2,7)
    # newJump(RETARROW1,2)
    # newJump(RETARROW1,5)
    # newJump(RETARROW1,7)
    # newJump(RETARROW1,9)
    # newJump(RETARROW2,1)
    # newJump(RETARROW2,5)
    # newJump(RETARROW2,8)

    newJump(RETARROW1,3)
    newJump(RETARROW1,8)

    print(findJump(GOARROW1,0))
    print(findJump(GOARROW1,3))
    print(findJump(GOARROW1,5))
    print(findJump(GOARROW1,8))
    print(findJump(GOARROW1,10))

    # print(findJump('start',0))
    # print(findJump('end',0))
    # print(findJump(GOARROW1,0))
    # print(findJump(GOARROW1,5))
    # print(findJump(RETARROW1,2))
    # print(findJump(RETARROW1,2,1))
    # print(findJump(RETARROW2,2))

    printJmpTab()
