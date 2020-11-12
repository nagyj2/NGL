# NGL Bytecode 2.1 Symbol Table

from copy import deepcopy
from enum import Enum
import bc2_1_sc as SC
from bc2_1_sc import INT, FLOAT, BOOL, STRING, NULL, ARRAY, LIST, GOARROW1, GOARROW2, RETARROW1, RETARROW2, RETURN, IDENT, USRFUNC, PRIMATIVE, COLLECTION, ARROWS, mark
import bc2_1_e as E
from bc2_1_e import Variable, Collection, SYMBOL

class NewType(Enum):        # Type of scope opem
    CLEAN = 1       # Create new, empty scope
    FUNCTION = 2    # Create clean scope, but add argument variables to spcTab

class CollapseType(Enum):   # Type of scope collapse
    DROP = 1        # Drop contents of highest scope
    MERGE = 2       # Scope contents are brought down, but dropping contents on name conflicts
    OVERRIDE = 3    # Scope contents are brought down, overriding on name conflict
    FUNCTION = 4    # Drop everything except for function result (stored in spcTab under _r)

class TableState():
    def __init__(self,symbols,jumps,special,usrfunc):
        self.symTab = deepcopy(symbols)
        self.jmpTab = deepcopy(jumps)
        self.spcTab = deepcopy(special)
        self.usrTab = deepcopy(usrfunc)

def init():
    global symTab, jmpTab, spcTab, usrTab, size
    symTab = [] # Symbols (Variables and Collections) -> User
    jmpTab = [] # Generic Jump Labels -> User
    spcTab = [] # Special Symbols, Arrow Jumps, Function arguments -> System
    usrTab = [] # Modules introduced by the user -> User
    size = 0 # Depth of symbol table

    newScope()

def save():
    global symTab, jmpTab, spcTab, usrTab
    state = TableState(symTab,jmpTab,spcTab,usrTab)
    return state

def load(state):
    global symTab, jmpTab, spcTab, usrTab, size

    symTab = state.symTab
    jmpTab = state.jmpTab
    spcTab = state.spcTab
    usrTab = state.usrTab
    size = len(symTab)

def printSymTab():
    global symTab
    for i, scope in enumerate(symTab):
        print('=Sym Scope '+str(i)+'=')
        for j, (n, v) in enumerate(scope.items()):
            print(n, ":", v)
    print()

def printJmpTab():
    global jmpTab
    for i, scope in enumerate(jmpTab):
        print('=Jmp Scope '+str(i)+'=')
        for j, (n, v) in enumerate(scope.items()):
            print(n, ":", v)
    print()

def printSpcTab():
    global spcTab
    for i, scope in enumerate(spcTab):
        print('=Spc Scope '+str(i)+'=')
        for j, (n, v) in enumerate(scope.items()):
            if v != None:
                if n == GOARROW1: n = '->'
                elif n == GOARROW2: n = '=>'
                elif n == RETARROW1: n = '<-'
                elif n == RETARROW2: n = '<='
                elif n == RETURN: n = '_r'
                print(n, ":", v)
            else: # Handle empty values in special tab
                pass
    print()

def printUsrTab():
    global usrTab
    for i, scope in enumerate(usrTab):
        print('=Usr Scope '+str(i)+'=')
        for j, (n, v) in enumerate(scope.items()):
            print(n, ":", v)
    print()

def printTab():
    printSymTab()
    printJmpTab()
    printSpcTab()
    printUsrTab()

def newScope(type1 = NewType.CLEAN, type2 = None, type3 = None, type4 = None, funcargs = None):
    global symTab, spcTab, jmpTab, usrTab, size
    # Will create a new scope for each table. Will assign default values to the special table

    if type2 == None: type2 = type1
    if type3 == None: type3 = type1
    if type4 == None: type4 = type1

    symTab.append({})
    jmpTab.append({})
    spcTab.append({ RETURN: Variable(NULL,None), GOARROW1: [], GOARROW2: [],
                    RETARROW1: [], RETARROW2: [] })
    usrTab.append({}) # Start with clean base
    if type3 == NewType.FUNCTION: #
        if funcargs == None or type(funcargs) != list:
            mark('function argument list must be provided for new function scope')
        else:
            for i in range(len(funcargs)):
                if type(funcargs[i]) in {Variable, Collection}: spcTab[-1]['arg'+str(i)] = deepcopy(funcargs[i])
                else:                                           mark('function arguments must be variables or collections')
    size += 1

def collapse(type1 = CollapseType.DROP, type2 = None, type3 = None, type4 = None):
    global symTab, spcTab, jmpTab, usrTab, size
    if size <= 1: mark('cannot collapse with one for fewer scopes'); return

    if type2 == None: type2 = type1
    if type3 == None: type3 = type1
    if type4 == None: type4 = CollapseType.MERGE # Assume user wants to accumulate modules

    _collapseTab(type1,symTab)
    _collapseTab(type2,jmpTab)
    _collapseTab(type3,spcTab) # FIX: The arrows should merge or drop and sort
    _collapseTab(type4,usrTab)

    _delScope()

def newSym(name, value, level = -1):
    global symTab
    level = __validateLevel(level)

    if type(value) not in SYMBOL:
        mark('values must be in variable or collection'); return
    elif name in symTab[level]:
        mark('variable already exists'); return
    symTab[level][name] = value

def setSym(name, value, index = -1, burrow = False, level = -1):
    global symTab, size
    # Note: index is an int
    # burrow = true will go down one scope if there is a name error
    # level is the level of symTab to check

    level = __validateLevel(level)
    error = False

    # TODO: Move to interpreter?
    if name == 'res' or name == RETURN:
        setSpc(RETURN, value, level)
        return

    if type(value) not in SYMBOL:
        mark('values must be in variable or collection'); return
    elif name not in symTab[level]:
        error = True
        if abs(level) == size: mark('variable does not exist'); return
    elif type(value) != type(symTab[level][name] and index < 0):
        mark('variables cannot change type'); return
    elif value.typ != symTab[level][name].typ:
        mark('variables cannot change primative type'); return

    if error and burrow:
        setSym(name, value, index, burrow, level - 1)
    elif type(symTab[level][name]) == Collection and index >= 0:
        symTab[level][name][index] = value # FIX - should use function
    else:
        _setTab(symTab[level], name, value)

def getSym(name, index = None, burrow = False, level = -1):
    global symTab, size
    level = __validateLevel(level)
    error = False

    # TODO: Make less of a hodge-podge fix?
    if name == 'res' or name == RETURN:
        return getSpc(RETURN, level = level)

    if name not in symTab[level]:
        error = True
        if abs(level) == size or not burrow:
            mark('variable does not exist')
            return Variable(NULL,None)

    if error and burrow:
        return getSym(name, index, burrow, level - 1)
    elif type(symTab[level][name]) == Collection and index != None:
        return symTab[level][name][index]
    elif type(symTab[level][name]) == Variable and index != None:
        mark('variables cannot be indexed')
        return
    else:
        return symTab[level][name]

def delSym(name, index = None, burrow = False, level = -1):
    global symTab, size
    level = __validateLevel(level)
    error = False

    if name not in symTab[level]:
        error = True
        if abs(level) == size or not burrow:
            mark('variable does not exist')
            return

    if error and burrow:
        delSym(name, index, burrow, level - 1)
    elif type(symTab[level][name]) == Collection and index != None:
        del symTab[level][name][index]
    elif type(symTab[level][name]) == Variable and index != None:
        mark('variables cannot be indexed')
        return
    else:
        del symTab[level][name]

def newJmp(name, value, level = -1):
    global jmpTab #, size
    level = __validateLevel(level)

    if type(value) != int:
        mark('jump location must be int'); return
    elif name in jmpTab[level]:
        mark('jump already exists'); return
    elif value < 0:
        mark('jump line must be positive'); return
    _setTab(jmpTab[level],name,value)

def getJmp(name, index = -1, burrow = False, level = -1):
    global jmpTab, size
    level = __validateLevel(level)
    error = False

    if name not in jmpTab[level]:
        error = True
        if abs(level) == size or not burrow:
            mark('jump does not exist')
            return Variable(NULL,None)

    if error and burrow:
        return getJmp(name, value, index, burrow, level - 1)
    return jmpTab[level][name]

def setSpc(name, value, level = -1):
    global spcTab #, size
    level = __validateLevel(level)

    if name in ARROWS:
        if type(value) != int:
            mark('arrow jump line must be int')
        elif value < 0:
            mark('arrow jump line must be positive')
        elif value in spcTab[level][name]:
            # Attempt to add existing location
            return
        else:
            spcTab[level][name].append(value)
            _sortTab(spcTab, name, level)
    elif name == RETURN:
        if type(value) not in SYMBOL:
            mark('return value must be a variable or collection')
        else:
            _setTab(spcTab[level], name, value)
    else:
        mark('unknown special symbol')

def getSpc(name, currline = -1, back = 0, level = -1):
    if name in {GOARROW1, GOARROW2}:
        array = spcTab[level][name]
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
        array = spcTab[level][name]
        for i in range(len(array)):
            if (array[i]>currline):
                return array[i-1-back]
        mark('no matching return arrow')
        return currline
    else:
        return spcTab[level][name]

def setUsr(name, value, level = -1):
    global usrTab #, size
    level = __validateLevel(level)

    if type(name) != str or value != USRFUNC:
        mark('name must be a string and value a USRFUNC token'); return
    else:
        usrTab[level][name] = value

def _delScope():
    global symTab, spcTab, jmpTab, usrTab, size
    if len(symTab) > 1:
        symTab.pop()
        jmpTab.pop()
        spcTab.pop()
        usrTab.pop()
        size -= 1
    else:
        mark('cannot remove bottom-most scope')

def _collapseTab(collapsetype, table):
    # CollapseType will determine how name conflicts will be determined
    if collapsetype == CollapseType.DROP: return
    for i, (name,elem) in enumerate(table[-1].items()):
        if collapsetype == CollapseType.FUNCTION:
            if name == RETURN:  _setTab(table[-2],name,elem) # Only carry over function return data
            else:               continue
        elif name in table[-2]:
            if collapsetype == CollapseType.MERGE:
                if name in ARROWS: # Merge by appending list
                    for arrow_dest in elem:
                        setSpc(name,arrow_dest,-2)
                    _sortTab(spcTab,name,-2)
                else: continue # Merge by ignoring conflicts
            elif collapsetype == CollapseType.OVERRIDE:
                _setTab(table[-2],name,elem)
            else: mark('invalid CollapseType for table collapse')
        else:
            _setTab(table[-2],name,elem)

def __validateLevel(level):
    global size
    # Ensure given level is valid. Convert it as needed
    # -1 is highest level, -2 second highest, ... , -size is lowest
    if level > 0: level *= -1 # Convert to negative if needed
    if abs(level) > size: mark('level does not exist'); return -1
    return level

def _setTab(table, name, elem):
    # Will force an addition (or override) in the specified table
    table[name] = elem

def _sortTab(table, name, level):
    # Sorts a list table -> used by spcTab
    table[level][name].sort()

if __name__ == '__main__':
    SC.init('var i::int 5;')
    init()

    newSym('first',Variable(INT,1))
    newSym('second',Variable(FLOAT,2))
    newSym('third',Variable(STRING,'3'))
    newJmp('label1',1)
    newJmp('label2',2)

    setSpc(GOARROW1,34)
    setSpc(GOARROW2,3)
    setSpc(RETARROW2,1)
    setSpc(RETARROW1,1)
    setSpc(RETARROW1,2)

    newScope()

    elem1 = [Variable(INT,1), Variable(INT,2),
             Variable(INT,3), Variable(INT,4)]

    newSym('fourth',Variable(INT,-3))
    newSym('fifth',Variable(BOOL,True))
    newSym('first',Variable(STRING,'10'))
    newSym('list',Collection(INT,elem1,LIST))
    newJmp('label1',10)
    newJmp('end',20)

    setSpc(GOARROW1,12)
    setSpc(GOARROW1,3)
    setSpc(RETARROW2,1)

    var1 = Variable(INT,10)
    var2 = Variable(INT,6)

    var3 = Variable(BOOL,True)
    var4 = Variable(BOOL,False)

    list1 = Collection(INT,[var1,var1,var2])

    print(- var1)
    print(var1 + var2)
    print(var1 - var2)
    print(var1 * var2)
    print(var1 / var2)
    print(var1 % var2)
    print(var1 ** var2)
    print(var3 and var4)
    print(var3 or var4)

    print(list1)
    print(list1 + var1)
    print(list1 + var2)
    print(list1 + list1)
    print(list1 - var1)
    print(list1 - var2)
    print(list1 - list1)

# var fixed::bool true;
# if fixed ->;
# print 'Enter a number between [1,99] for the computer to guess';
# read num::int;
# goto ~->;
# <-
# var num::int 42;
# <-
# var guess::int 50;
# var isHigher::bool false;
#
# incl length;
#
# if num < 1  end;
# if num > 99 end;
#
# print 'Begin Game!';
# print guess;
# goto guesslogic;
#
# feedback:
# if num > guess ->;
# set isHigher false;
# goto genguess;
#
# <- set isHigher true;
#
# genguess:
# if isHigher ->;
# set guess guess - (guess/2)::int;
# goto =>;
# <- set guess guess + (guess/2)::int;
# <= print guess;
#
# guesslogic:
# if guess > num goDown;
# if guess < num goUp;
# goto end;
# goDown: print 'Lesser';
# goto feedback;
# goUp: print 'Greater';
# goto feedback;
#
# end:
# print 'Finish!';
