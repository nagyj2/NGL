# NGL Bytecode 3.0 Logging Module
# Provides facilities for logging in all other modules

import logging

# TODO: move all logging to functions originating here
# i.e. get rid of mark!!
# TODO: for type checks, put all type errors into the logs

open = []

class LoggerDummy:
    def __init__(self):
        pass
    def debug(self,msg):
        pass
    def info(self,msg):
        pass
    def warning(self):
        pass
    def error(self):
        pass
    def critical(self):
        pass

def _initLogger(category,masterLevel,fileLevel,streamLevel,filename):
    # Creates and sets up a logging object and then returns it
    logger = logging.getLogger(category)
    logger.setLevel(masterLevel)
    mode = 'w' if len(open) == 0 else 'a' # for debugging, easier to have 1 log
    fh = logging.FileHandler('_{0}.log'.format(filename),mode) # handler for log file
    fh.setLevel(fileLevel)
    sh = logging.StreamHandler() # handler for console stream
    sh.setLevel(streamLevel)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    sh.setFormatter(formatter)
    logger.addHandler(fh)
    logger.addHandler(sh)
    open.append(category)
    logger.info('==Started logging {0}==='.format(category))
    return logger

def getLogger(category='master',masterLevel=logging.INFO,fileLevel=logging.INFO,streamLevel=logging.CRITICAL,filename='master'):
    # If logger is not open, it is initialized. If it is open, simply return
    # instance of respective logger
    global open

    if category == 'dummy':
        return LoggerDummy()

    elif category in open:
        return logging.getLogger(category)

    return _initLogger(category,masterLevel,fileLevel,streamLevel,filename)

if __name__ == '__main__':
    log1 = getLogger('test',logging.INFO,logging.INFO,logging.WARNING)
    log2 = getLogger('test',logging.WARNING,logging.INFO,logging.WARNING)
    log3 = getLogger('dummy')

    log1.info('test ma log')
    log2.info('logloglog')
    log3.info('dummy')
