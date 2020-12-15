# NGL Bytecode 2.1 Preprocessor

import bc2_1_sc as SC
from bc2_1_sc import mark
import bc2_1_st as ST
import bc2_1_sk as PPG
import bc2_1_i as I

def init(fname, src = None, debug = False):
    # global modules
    # Perform setup in one pass

    # If just filename is given, load source from file
    if src == None:
        src = _readSource(fname)

    # Initialize symbol table depending on if function call
    SC.init(fname,src)
    ST.init()

    isError = _grammarcheck(fname, src, debug = debug)

    # Save state from first pass
    SC_state = SC.save()
    ST_state = ST.save()

    # Load state
    # SC.load(SC_state)
    SC.reset() # Reset for proper readthrough by interpreter
    ST.load(ST_state) # Load initial values of symbol table

    return SC.error or isError

def func(fname, src = None, args = [], debug = False):
    # If just filename is given, load source from file

    # Save scanner state
    SC_state = SC.save()

    if src == None:
        src = _readSource(fname)

    ST.newScope(ST.NewType.FUNCTION, funcargs = args) # Create new function scope

    isError = _grammarcheck(fname, src, debug)

    if not isError:
        SC.reset() # Reset scanner for execution of tile
        SC.suppress = SC_state.suppress
        # print(SC_state.suppress)
        I.execute(stats = debug) #, isFunc = True, debug = True)

    ST.collapse(ST.CollapseType.DROP, type3 = ST.CollapseType.FUNCTION)

    # Load scanner state
    SC.load(SC_state)
    # SC.index-=1


def _readSource(fname):
    source = ''
    with open(fname+'.ngl','r') as reader:
        for line in reader.readlines():
            source += line
    return source

def _grammarcheck(fname, src = None, debug = False):
    if src == None:
        src = _readSource(fname)

    SC.init(fname, src)
    # Expects ST to be created
    PPG.execute()
    return SC.error

if __name__ == '__main__':
    fname = 'usr'
    src = ''
    with open(fname+'.ngl','r') as reader:
        for src_line in reader.readlines():
            src += src_line

    init(fname, src, debug = True)

    ST.printTab()
