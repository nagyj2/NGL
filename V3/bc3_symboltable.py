# NGL Bytecode 3.0 Symbol Table
# Designed so that there is only one symbol table for a single execution

from bc3_scanner import ScannerDummy, INT, FLOAT, BOOL, STR, NONE, ARRAY, LIST, GOARROW1, GOARROW2, RETARROW1, RETARROW2, ARROWS, IDENT
from bc3_logging import getLogger

sym_logger = getLogger('dummy')
linked = ScannerDummy()

def init(log=True):
    # Sets up the module to work. Also resets the module to its initial state
    global symTab, jmpTab, spcTab, size, linked, sym_logger
    symTab = [] # Symbols (Named Constants, Variables, Functions) -> User
    jmpTab = [] # Generic Jump Labels -> User
    spcTab = [] # Special Symbols, Arrow Jumps, Function arguments -> System
    size = 0 # Depth of symbol table
    newScope()

    if log: sym_logger = getLogger('symboltable')

def updateLink(scanner):
    # Display errors with the currently linked parser object
    global linked
    linked = scanner

def strTab(choice=('sym','jmp','spc')):
    global symTab, jmpTab, spcTab
    tabs,strep = [], ''
    if 'sym' in choice: tabs.append(symTab)
    if 'jmp' in choice: tabs.append(jmpTab)
    if 'spc' in choice: tabs.append(spcTab)
    if tabs == []:      tabs, choice = [symTab,jmpTab,spcTab], ('sym','jmp','spc')

    for tab,name in enumerate(choice):
        for scope,space in enumerate(tabs[tab]):
            strep += '={0}Tab Scope {1}=\n'.format(name,scope)
            for j, (n, v) in enumerate(space.items()):
                if v != None:
                    if n == GOARROW1: n = '->'; v = [x+1 for x in v] # add 1 so it matches text editor lines
                    elif n == GOARROW2: n = '=>'; v = [x+1 for x in v] # add 1 so it matches text editor lines
                    elif n == RETARROW1: n = '<-'; v = [x+1 for x in v] # add 1 so it matches text editor lines
                    elif n == RETARROW2: n = '<='; v = [x+1 for x in v] # add 1 so it matches text editor lines
                    elif name == 'jmp': v += 1
                    strep += '{0} : {1}\n'.format(n, v)
                else: # Handle empty values in special tab
                    pass
        strep += '\n'
    return strep

def printTab(choice=('sym','jmp','spc')):
    print(strTab(choice))

def newScope():
    global symTab, spcTab, jmpTab, size
    # Will create a new scope for each table. Will assign default values to the special table

    symTab.append({})
    jmpTab.append({})
    spcTab.append({ GOARROW1: [], GOARROW2: [],
                    RETARROW1: [], RETARROW2: [] })
    size += 1
    sym_logger.debug('new scope')

def __validateLevel(level):
    global size, linked
    # Ensure given level is valid. Convert it as needed
    # -1 is highest level, -2 second highest, ... , -size is lowest
    if level > 0: level *= -1 # Convert to negative if needed
    if abs(level) > size:
        linked.mark('level does not exist',logger=sym_logger)
        return -1
    return level

def newSym(name, value, level=-1):
    global symTab, linked
    level = __validateLevel(level)

    if name in symTab[level]:
        linked.mark('variable already exists',logger=sym_logger)
        return

    symTab[level][name] = value
    sym_logger.debug('new {0} set to {1}'.format(name,value))

def setSym(name, value, level=-1, burrow=False):
    global symTab, size, linked
    level = __validateLevel(level)

    if name not in symTab[level]:
        if abs(level) == size:  sym_logger.warning('variable {0} does not exist'.format(name),logger=sym_logger)
        elif burrow:            setSym(name,value,level-1,burrow)
    else:
        symTab[level][name] = value
        sym_logger.debug('set {0} to {1}'.format(name,value))

def getSym(name, level=-1, burrow=False):
    global symTab, size, linked
    level = __validateLevel(level)

    if name not in symTab[level]:
        if abs(level) == size:  sym_logger.mark('variable {0} does not exist'.format(name),logger=sym_logger)
        elif burrow:            return getSym(name,level-1,burrow)
    else:
        return symTab[level][name]

def delSym(name, level=-1, burrow=False):
    global symTab, size, linked
    level = __validateLevel(level)

    if name not in symTab[level]:
        if abs(level) == size:  linked.mark('variable {0} does not exist'.format(name),logger=sym_logger)
        elif burrow:            getSym(name,level-1,burrow)
    else:
        del symTab[level][name]
        sym_logger.debug('deleted {0}'.format(name))

def newJmp(name, value, level=-1):
    global jmpTab, size, linked
    level = __validateLevel(level)

    if name in jmpTab[level]:
        linked.mark('label already exists',logger=sym_logger)
        return

    jmpTab[level][name] = value
    sym_logger.debug('new label {0} set to {1}'.format(name,value))

def getJmp(name, level=-1, burrow=False):
    global jmpTab, size, linked
    level = __validateLevel(level)

    if name not in jmpTab[level]:
        if abs(level) == size:  linked.mark('label {0} does not exist'.format(name),logger=sym_logger)
        elif burrow:            return getJmp(name,level-1,burrow)
    else:
        return jmpTab[level][name]

def setSpc(name, value, level=-1):
    global spcTab, size, linked
    level = __validateLevel(level)

    if name in ARROWS:
        jumps = spcTab[level][name] # list of jump spots
        if value in jumps or value < 0:  return

        jumps.append(value)
        jumps.sort()
        sym_logger.debug('added to arrow {0} with {1}'.format(name,value))
    else:
        linked.mark('unknown spcTab symbol {0}'.format(name),logger=sym_logger)

def getSpc(name, level=-1, burrow=False):
    global spcTab, size, linked
    level = __validateLevel(level)

    if name not in spcTab[level]:
        if abs(level) == size:  linked.mark('special data {0} does not exist'.format(name),logger=sym_logger)
        elif burrow:            return getSpc(name,level-1,burrow)
    else:
        return spcTab[level][name]

def getNextArrow(name, currline, back=0, level=-1):
    # name is the arrow to match, back is how many arrows to advance
    # TODO ERROR: what if jumps is []?
    global spcTab, linked

    if name in (RETARROW1, RETARROW2):
        jumps, lastGreater = spcTab[level][name], False
        for i in range(len(jumps)):
            if (not lastGreater and jumps[i]>currline):
                lastGreater=True
            elif (lastGreater and jumps[i]>currline):
                try:                return jumps[i-1+back]
                except IndexError:  linked.mark('cannot go further',logger=sym_logger); return currline
        try:                return jumps[-1+back]
        except IndexError:  linked.mark('cannot go further',logger=sym_logger); return currline
    elif name in (GOARROW1, GOARROW2):
        jumps = spcTab[level][name]
        for i in range(len(jumps)):
            if (jumps[i]>=currline): # >= means you skip current line. > means you dont
                if i-1-back < 0:    linked.mark('cannot go further',logger=sym_logger); return currline
                else:               return jumps[i-1-back]
        linked.mark('no matching return arrow',logger=sym_logger)
    else:
        linked.mark('requested non-arrow',logger=sym_logger)
    return currline

def collapse(symType='drop', jmpType='drop', spcType='drop'):
    # TODO: Implement type -> need DROP, MERGE and OVERWRITE
    global symTab, spcTab, jmpTab, size, linked
    if size <= 1: linked.mark('cannot collapse last scope',logger=sym_logger); return

    _collapseTab(symType, symTab)
    _collapseTab(jmpType, jmpTab)
    _collapseTab(spcType, spcTab) # FIX: The arrows should merge or drop and sort

    _delScope()
    sym_logger.debug('deleted scope')

def _delScope():
    global symTab, spcTab, jmpTab, size
    symTab.pop()
    jmpTab.pop()
    spcTab.pop()
    size -= 1

def _collapseTab(type, table):
    # CollapseType will determine how name conflicts will be determined
    if type == 'drop': return
    for name, elem in table[-1].items(): # for elements in tab
        if name in table[-2]: # name conflict
            if type == 'override':
                table[-2][name] = elem
        else: # add element to previous table
            table[-2][name] = elem



# Function for inserting vars and vals important for subcalls (like args and return val)
