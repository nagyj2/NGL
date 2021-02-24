# NGL Bytecode 3.0 Preprocessor
# Performs required work before execution

import bc3_scanner as SC
import bc3_grammar as PG
import logging

def initLogging():
    global logger
    logger.setLevel(logging.INFO)
    fh = logging.FileHandler('processor.log') # handler for log file
    fh.setLevel(logging.INFO)
    sh = logging.StreamHandler() # handler for console stream
    sh.setLevel(logging.WARNING)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    sh.setFormatter(formatter)
    logger.addHandler(fh)
    logger.addHandler(sh)

    logger.info('initialized preprocessor on file %s' % filename)

def init(filename, log = False):
    logger = logging.getLogger('processor')
    if log:         initLogging()

    src = open(file).readlines()

    SC.init(filename,src)
    # ST.init()

    passOne(log=log)


# Runs a grammar check on the source code
def passOne(log=False):
    # Requires SC and ST to have been initialized
    pass

# Actually executes the code
def passTwo(log=False):
    # Requires SC and ST to have been initialized
    pass
