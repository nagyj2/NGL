# NGL Bytecode 3.0 Symbol Table
# Designed so that there is only one symbol table for a single execution

from bc3_scanner import ScannerDummy, INT, FLOAT, BOOL, STR, NONE, ARRAY, LIST, GOARROW1, GOARROW2, RETARROW1, RETARROW2, ARROWS, IDENT
from bc3_logging import getLogger
from copy import deepcopy

_logger = getLogger('dummy')
linked = ScannerDummy()

# Symbol table has values
    # constants -> values
    # variables -> reference by default (value can be called when needed)
    # functions -> file to call
    # labels -> line number

def init(log=True):
    # Sets up the module to work. Also resets the module to its initial state
    global symTab, spcTab, size, linked, _logger
    symTab = [] # Symbols (Named Constants, Variables, Functions) -> User
    spcTab = [] # Special Symbols, Arrow Jumps, Function arguments -> System
    size = 0 # Depth of symbol table
    newScope()

    if log: _logger = getLogger('symboltable')

def export():
    # Returns current scope only
    global symTab, spcTab
    return (deepcopy(symTab[-1]),deepcopy(spcTab[-1]))

def load(tabs):
    # Overrides current scope
    global symTab, spcTab
    symTab[-1] = tabs[0]
    spcTab[-1] = tabs[1]

def updateLink(scanner):
    # Display errors with the currently linked parser object
    global linked
    linked = scanner

def strTab(choice=('sym','spc')):
    global symTab, spcTab
    tabs,strep = [], ''
    if 'sym' in choice: tabs.append(symTab)
    if 'spc' in choice: tabs.append(spcTab)
    if tabs == []:      tabs, choice = [symTab,spcTab], ('sym','spc')

    for tab,name in enumerate(choice):
        for scope,space in enumerate(tabs[tab]):
            strep += '={0}Tab Scope {1}=\n'.format(name,scope)
            for j, (n, v) in enumerate(space.items()):
                if v != None:
                    if n == GOARROW1: n = '->'; v = [x+1 for x in v] # add 1 so it matches text editor lines
                    elif n == GOARROW2: n = '=>'; v = [x+1 for x in v] # add 1 so it matches text editor lines
                    elif n == RETARROW1: n = '<-'; v = [x+1 for x in v] # add 1 so it matches text editor lines
                    elif n == RETARROW2: n = '<='; v = [x+1 for x in v] # add 1 so it matches text editor lines
                    strep += '{0} : {1}\n'.format(n, v)
                else: # Handle empty values in special tab
                    pass
        strep += '\n'
    return strep

def printTab(choice=('sym','spc')):
    print(strTab(choice),end='')

def newScope():
    global symTab, spcTab, size
    # Will create a new scope for each table. Will assign default values to the special table

    symTab.append({})
    spcTab.append({ GOARROW1: [], GOARROW2: [],
                    RETARROW1: [], RETARROW2: [] })
    size += 1
    _logger.debug('new scope')

def __validateLevel(level):
    global size, linked
    # Ensure given level is valid. Convert it as needed
    # -1 is highest level, -2 second highest, ... , -size is lowest
    if level > 0: level *= -1 # Convert to negative if needed
    if abs(level) > size:
        _logger.warning('level does not exist, returned {0}'.format(-1))
        return -1
    return level

def newSym(name, value, level=-1):
    global symTab, linked
    level = __validateLevel(level)

    if name in symTab[level]:
        _logger.warning('symbol already declared, got {0}'.format(name))
        return

    symTab[level][name] = value
    _logger.debug('new symbol {0} set to {1}'.format(name,value))

def setSym(name, value, level=-1, burrow=False):
    global symTab, size, linked
    level = __validateLevel(level)

    if name not in symTab[level]:
        if abs(level) == size:  _logger.warning('symbol not declared, got {0}'.format(name))
        elif burrow:            _logger.info('symbol not found on level {0}, burrowing...'.format(name)); setSym(name,value,level-1,burrow)
    else:
        symTab[level][name] = value
        _logger.debug('set symbol {0} to {1}'.format(name,value))

def getSym(name, level=-1, burrow=False):
    global symTab, size, linked
    level = __validateLevel(level)

    if name not in symTab[level]:
        if abs(level) == size:  _logger.error('symbol not declared, got {0}'.format(name))
        elif burrow:            _logger.info('symbol not found on level {0}, burrowing...'.format(name)); return getSym(name,level-1,burrow)
    else:
        _logger.debug('returned symbol {0} as {1}'.format(name,symTab[level][name]))
        return symTab[level][name]

def hasSym(name, level=-1, burrow=False):
    global symTab, size, linked
    level = __validateLevel(level)

    if name not in symTab[level]:
        if abs(level) == size:  return False
        elif burrow:            return hasSym(name,level-1,burrow)

    return name in symTab[level]

def delSym(name, level=-1, burrow=False):
    global symTab, size, linked
    level = __validateLevel(level)

    if name not in symTab[level]:
        if abs(level) == size:  _logger.mark('symbol not declared, got {0}'.format(name))
        elif burrow:            _logger.info('symbol not found on level {0}, burrowing...'.format(name)); getSym(name,level-1,burrow)
    else:
        del symTab[level][name]
        _logger.debug('deleted symbol {0}'.format(name))

def setSpc(name, value, level=-1):
    global spcTab, size, linked
    level = __validateLevel(level)

    if name in ARROWS:
        jumps = spcTab[level][name] # list of jump spots
        if value in jumps or value < 0:  _logger.debug('skipped arrow add to {0}'.format(name)); return

        jumps.append(value)
        jumps.sort()
        _logger.debug('added to arrow {0} with {1}'.format(name,value))
    else:
        _logger.mark('unknown special symbol, got {0}'.format(name))

def getSpc(name, level=-1, burrow=False):
    global spcTab, size, linked
    level = __validateLevel(level)

    if name not in spcTab[level]:
        if abs(level) == size:  linked.mark('special symbol not declared, got {0}'.format(name),logger=_logger)
        elif burrow:            _logger.info('special symbol not found on level {0}, burrowing...'.format(name)); return getSpc(name,level-1,burrow)
    else:
        _logger.debug('returned special symbol {0} as {1}'.format(name,spcTab[level][name]))
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
                except IndexError:  _logger.warning('arrow cannot be found, returning {0}'.format(currline)); return currline
        try:                return jumps[-1+back]
        except IndexError:  _logger.warning('arrow cannot be found, returning {0}'.format(currline)); return currline
    elif name in (GOARROW1, GOARROW2):
        jumps = spcTab[level][name]
        for i in range(len(jumps)):
            if (jumps[i]>=currline): # >= means you skip current line. > means you dont
                if i-1-back < 0:    _logger.warning('arrow cannot be found, returning {0}'.format(currline)); return currline
                else:               return jumps[i-1-back]
        _logger.warning('arrow cannot be found, returning {0}'.format(currline))
    else:
        _logger.warning('expected arrow, got {0}. returning {0}'.format(name,currline))
    return currline

def collapse(symType='drop', spcType='drop'):
    # TODO: Implement type -> need DROP, MERGE and OVERWRITE
    global symTab, spcTab, size, linked
    if size <= 1: _logger.warning('cannot collapse last scope'); return

    _collapseTab(symType, symTab)
    _collapseTab(spcType, spcTab) # FIX: The arrows should merge or drop and sort

    _delScope()
    _logger.debug('deleted scope')

def _delScope():
    global symTab, spcTab, size
    symTab.pop()
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
