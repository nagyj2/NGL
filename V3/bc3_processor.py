# NGL Bytecode 3.0 Preprocessor
# Performs required work before execution

from bc3_scanner import Scanner
import bc3_grammar as PG

def init(filename, log = True):
    # if log:         initLogging()

    src = open(file).readlines()

    SC = Scanner(filename,src,log)
    # ST.init()

    passOne(log=log)


# Runs a grammar check on the source code
def passOne(log=True):
    # Requires SC and ST to have been initialized
    pass

# Actually executes the code
def passTwo(log=True):
    # Requires SC and ST to have been initialized
    pass
