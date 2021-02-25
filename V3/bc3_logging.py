# NGL Bytecode 3.0 Logging Module
# Provides facilities for logging in all other modules

import logging

def initLogging(self):
    global logger
    logger.setLevel(logging.INFO)
    fh = logging.FileHandler('_symboltable.log') # handler for log file
    fh.setLevel(logging.INFO)
    sh = logging.StreamHandler() # handler for console stream
    sh.setLevel(logging.WARNING)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    sh.setFormatter(formatter)
    logger.addHandler(fh)
    logger.addHandler(sh)

    logger.info('initialized symbol table on file %s' % self.fname)
