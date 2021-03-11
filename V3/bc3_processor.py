# NGL Bytecode 3.0 Preprocessor
# Performs required work before execution

from bc3_logging import getLogger
from bc3_scanner import Scanner
import bc3_symboltable as ST
import bc3_grammar as PG
import logging

_initialized = False
pre_logger = getLogger('dummy')

def init(log = True):
    # Initialize the preprocessor
    global pre_logger, _initialized

    if log: pre_logger = getLogger('preprocessor')

    ST.init()

    _initialized = True

def execute(filename, log=True):
    # Parse and execute a file
    global pre_logger, _initialized

    if not _initialized: raise Exception('proprocessor not initialized')

    src = "".join(open(filename).readlines()) # Create complete string representing code
    pre_logger.debug('sucessfully read source')

    pre_logger.info('starting scanner')
    SC = Scanner(filename,src,log)
    ST.updateLink(SC)
    _passOne(SC, log=log)
    _passTwo(SC, log=log)


def _passOne(scanner, log=True):
    global pre_logger
    # Runs a grammar check on the source code
    # Requires SC and ST to have been initialized

    ST.newScope()

    pre_logger.info('starting grammar check of {0}'.format(scanner.fname))
    PG.execute(scanner, log)


    state = ST.export()
    ST.collapse()

    ST.load(state)
    ST.printTab(['sym'])

def _passTwo(scanner, log=True):
    global pre_logger
    # Actually executes the code
    # Requires SC and ST to have been initialized
    pass

if __name__ == '__main__':
    init(True)

    execute('test.ngl')
