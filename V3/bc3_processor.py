# NGL Bytecode 3.0 Preprocessor
# Performs required work before execution

from bc3_logging import getLogger
from bc3_scanner import Scanner
import bc3_symboltable as ST
import bc3_grammar as PG
import logging

# TODO: when calling functions, pass info to next/ restore old variables
initialized = False
pre_logger = getLogger('dummy')
savedStates = {}

def _pre_execute(filename, log=True):
    global pre_logger
    src = "".join(open(filename).readlines()) # Create complete string representing code
    pre_logger.debug('sucessfully read source')

    scan = Scanner(filename,src,log)
    ST.updateLink(scan)
    return scan

def execute_main_grammar(filename, log=True):
    # Parse and execute a file
    global pre_logger, initialized, savedStates

    if log: pre_logger = getLogger('preprocessor')

    ST.init()
    ST.newScope()

    scan = _pre_execute(filename,log)

    # === Pass One ===
    pre_logger.info('starting grammar check of {0}'.format(scan.fname))
    print('>',len(savedStates))
    PG.execute(scan, log=log)
    ST.save(filename)

    pre_logger.info('finished grammar check')
    pre_logger.info('expanded scopes {0}'.format(ST.saveNames()))

    # print('==={0}==='.format(filename))
    # for key,val in state.items(): print(key)
    ST.printTab(['sym'])
    # ST.collapse() # TODO: Alter state for pass 2
    # ST.load(state)

    # === Pass Two ===
    pass

def execute_function_grammar(filename, state, log=True):
    # Parse and execute a file
    global pre_logger, initialized, savedStates

    if log: pre_logger = getLogger('preprocessor')
    scan = _pre_execute(filename,log)

    # === Pass One ===
    ST.newScope()
    pre_logger.info('starting grammar check of {0}'.format(scan.fname))

    PG.execute(scan, log)
    ST.save(filename)


    # print('==={0}==='.format(filename))
    # for key,val in savedStates.items(): print(key)
    ST.printTab(['sym'])
    ST.collapse('function') # TODO: Alter state for pass 2
    # state = ST.export()
    # ST.load(state)

    # === Pass Two ===
    pass

if __name__ == '__main__':
    # global initialized, pre_logger, savedStates
    from sys import argv
    savedStates = {} # store the loopup tables for called functions


    execute_main_grammar(argv[1])
