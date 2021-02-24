# NGL Bytecode 3.0 Scanner

import logging

# Operators
ENOT = 1 # ><
PARAM = 2 # @
OR = 3 # |
UNION = 4 # ||
AND = 5 # &
INTER = 6 # &&
EQ = 7 # =
NE = 8 # <>
LT = 9 # <
GT = 10 # >
PLUS = 11 # +
MINUS = 12 # -
MULT = 13 # *
DIV = 14 # /
INTDIV = 15 # \
MOD = 16 # %
EXP = 17 # ^
NOT = 18 # !
CAST = 19 # ::

# Keywords
VAR = 30 # var
CONST = 31 # const
READ = 32 # in
SET = 33 # set
DEL = 34 # del
GOTO = 35 # goto
IF = 36 # if
TRY = 37 # try
EXEC = 38 # cmp
PRINT = 39 # out
INCLUDE = 40 # incl
QUIT = 41 # quit
RETURN = 42 # retn (TBD)
RAISE = 43 # flag (TBD)
LOG = 44 # log (TBD)

# Arrows
GOARROW1 = 60 # ->
GOARROW2 = 61 # =>
RETARROW1 = 62 # <-
RETARROW2 = 63 # <=
ARROWSHAFT = 64 # ~
NOJUMP = 65 # .

# Brackets
LPAREN = 70 # (
RPAREN = 71 # )
LBRAK = 72 # [
RBRAK = 73 # ]
LCURLY = 74 # {
RCURLY = 75 # }

# Syntax Markers
COMMA = 76 # ,
COLON = 77 # :
LINEEND = 78 # ; or \n

# Types
INT = 80 # int
STR = 81 # str
FLOAT = 82 # float
BOOL = 83 # bool
ARRAY = 84 # array
LIST = 85 # list
NONE = 86 # null (TBD)

# Literals
NUMBER = 90 # integer number
DECIMAL = 91 # float number (TBD)
STRING = 92 # string
IDENT = 93 # identifier

# Utility
EOF = 99 # end of file marker

KEYWORDS = {'int': INT, 'float': FLOAT, 'bool': BOOL, 'str': STR,
    'array': ARRAY, 'list': LIST, 'null': NONE, 'var': VAR, 'const': CONST,
    'in': READ, 'set': SET, 'del': DEL, 'goto': GOTO, 'if': IF, 'try': TRY,
    'cmp': EXEC,  'out': PRINT, 'incl': INCLUDE, 'quit': QUIT, 'retn': RETURN,
    'flag': RAISE, 'log': LOG}

# Initializes scanner for new source code
def init(file, src = None, log = True):
    global logger, line, lastline, errline, pos, lastpos, errpos, filename
    global sym, val, error, source, index, jump, newline, suppress

    if src == None: src = open(file).readlines()

    line, lastline, errline = 0, 0, 0 # current line, previous line, last error line
    pos, lastpos, errpos = 0, 0, 0 # current pos in line, previous position, last error position
    sym, val = None, None # current symbol, value associated with symbol
    source, index = src, 0 # raw code, index in line, current line index in source
    jump, newline, filename = False, 0, file # jump on new line, line to jump to, file name
    error, suppress = False, False # error detected, supress detected errors
    getChar(); getSym() # Load initial character and get symbol

    logger = logging.getLogger('scanner')
    if log:         initLogging()

def initLogging():
    global logger, filename
    logger.setLevel(logging.INFO)
    fh = logging.FileHandler('scanner.log') # handler for log file
    fh.setLevel(logging.INFO)
    sh = logging.StreamHandler() # handler for console stream
    sh.setLevel(logging.WARNING)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    sh.setFormatter(formatter)
    logger.addHandler(fh)
    logger.addHandler(sh)

    logger.info('initialized scanner on file %s' % filename)

# Resets entire scanner state
def reset():
    global line, lastline, errline, pos, lastpos, errpos
    global sym, val, error, index, jump, newline, suppress, logger
    # Reinitializes scanner for current source
    line, lastline, errline = 0, 0, 0
    pos, lastpos, errpos = 0, 0, 0
    sym, val = None, None
    index = 0
    jump, newline = False, 0
    error, suppress = False, False
    getChar(); getSym()

    logger.info('reinitialized scanner on file %s' % filename)

# Resets all parsing variables to be at the beginning of a specified line
def resetLine(setline):
    global line, lastline, errline, pos, lastpos, errpos
    global sym, val, error, index, jump, newline, suppress
    # Reinitializes scanner for current source
    line, lastline, errline = setline, setline, setline
    pos, lastpos, errpos = 0, 0, 0
    sym, val = None, None
    index = 0
    jump, newline = False, 0

    logger.info('jumped execution to line %s' % line)

# Marks an error and sets error flag to true
def mark(msg):
    global errline, errpos, error, suppress, filename
    error = True
    if not suppress:
        if lastline > errline or lastpos > errpos:
            print('file',filename,'error: line', lastline+1, 'pos', lastpos, msg)
            logger.error('file',filename,'error: line', lastline+1, 'pos', lastpos, msg)
        errline, errpos = lastline, lastpos

# Sets a specific line to jump to when the current line is fully parsed
def setGoto(jump_line):
    global jump, newline
    jump, newline = True, jump_line

# Executes the line jump
def execGoto():
    global index, source
    resetline(newline)

    # FIX: may be broken
    for i,src_line in enumerate(source.splitlines()):
        if i == newline: break
        else: index += len(src_line)+1 # Include newline

    getChar(); getSym()

# Jumps to the next source line
# Executed after an accepted parse of LINEEND
def nextLine():
    global line, pos
    pos, line = 0, line + 1

# Parses a number to a integer or float
def number():
    global sym, val
    sym, val, div = NUMBER, 0, 10
    while '0' <= ch <= '9':
        val = 10 * val + int(ch)
        getChar()
    if ch == '.':
        getChar()
        sym = DECIMAL
        while '0' <= ch <= '9':
            val =  val + int(ch) / div
            getChar(); div /= 10

    logger.debug('parsed number %s' % val)
    if val >= 2**31:
        mark('number too large'); val = 0
    elif val <= 2**-31:
        mark('number too small'); val = 0


# Parses a string
def string(open):
    global logger, sym, val
    getChar()
    start = index - 1
    while chr(0) != ch != open: getChar()
    if ch == chr(0): mark('string not terminated'); sym = None;
    else:
        sym = STRING; val = source[start:index-1]
        getChar(); # Get rid of ending '

        logger.debug('parsed string %s' % filename)

# Parses a word as either a keyword or identifier
def identKW():
    global sym, val
    start = index - 1
    while ('A' <= ch <= 'Z') or ('a' <= ch <= 'z') or ('0' <= ch <= '9') or (ch == '_'): getChar()
    val = source[start:index-1]
    sym = KEYWORDS[val] if val in KEYWORDS else IDENT

    logger.debug('parsed %s as %s' % (val,sym))

# Keeps taking inputs until the end comment marker is found
def blockcomment():
    logger.debug('found block comment')
    while chr(0) != ch:
        if ch == '*':
            getChar()
            if ch == '/':
                 getChar(); break
        else:
            getChar()
    if ch == chr(0): mark('comment not terminated')
    else: getChar()

# Keeps taking inputs until a newline or EOF is found
def linecomment():
    global logger
    logger.debug('found line comment')
    while chr(0) != ch != '\n': getChar()


# Retrieves the next character in the input (does not consume input)
# Jumps lines as required
def getChar():
    global line, lastline, pos, lastpos, ch, index
    if index == len(source): ch = chr(0)
    else:
        ch, index = source[index], index + 1
        lastpos = pos
        # if ch == '\n':
        #     pos, line = 0, line + 1
        # else:
        lastline, pos = line, pos + 1


# Determines the next symbol in the input
def getSym():
    global logger, sym, jump, source

    while chr(0) < ch <= ' ' and ch != '\n':
        getChar()

    if 'A' <= ch <= 'Z' or 'a' <= ch <= 'z' or ch == '_': identKW()
    elif ch == "'" or ch == '"': string(ch)
    elif '0' <= ch <= '9': number()

    elif ch == '>':
        getChar()
        if ch == '<': getChar(); sym = ENOT
        else: sym = GT
    elif ch == '@': getChar(); sym = PARAM
    elif ch == '|':
        getChar()
        if ch == '|': getChar(); sym = UNION
        else: sym = OR
    elif ch == '&':
        getChar()
        if ch == '&': getChar(); sym = INTER
        else: sym = AND
    elif ch == '=':
        getChar()
        if ch == '>': getChar(); sym = GOARROW2
        else: sym = EQ
    elif ch == '<':
        getChar()
        if ch == '-': getChar(); sym = RETARROW1
        elif ch == '=': getChar(); sym = RETARROW2
        elif ch == '>': getChar(); sym = NE
        else: sym = LT
    elif ch == '+': getChar(); sym = PLUS
    elif ch == '-':
        getChar()
        if ch == '>': getChar(); sym = GOARROW1
        else: sym = MINUS
    elif ch == '*': getChar(); sym = MULT
    elif ch == '/':
        getChar();
        if ch == '/': getChar(); linecomment(); getSym()
        elif ch == '*': getChar(); blockcomment(); getSym()
        else: sym = DIV
    elif ch == '\\': getChar(); sym = INTDIV
    elif ch == '%': getChar(); sym = MOD
    elif ch == '^': getChar(); sym = EXP
    elif ch == '!': getChar(); sym = NOT
    elif ch == ':':
        getChar();
        if ch == ':': getChar(); sym = CAST
        else: sym = COLON
    elif ch == '~': getChar(); sym = ARROWSHAFT
    elif ch == '.': getChar(); sym = NOJUMP
    elif ch == '(': getChar(); sym = LPAREN
    elif ch == ')': getChar(); sym = RPAREN
    elif ch == '[': getChar(); sym = LBRAK
    elif ch == ']': getChar(); sym = RBRAK
    elif ch == '{': getChar(); sym = LCURLY
    elif ch == '}': getChar(); sym = RCURLY
    elif ch == ',': getChar(); sym = COMMA
    elif ch == ';': getChar(); sym = LINEEND
    elif ch == '\n': getChar(); sym = LINEEND
    elif ch == chr(0): sym = EOF
    else: mark('illegal character: '+ch); getChar(); sym = None
