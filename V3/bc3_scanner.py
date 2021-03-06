# NGL Bytecode 3.0 Scanner
# Designed so that there can be multiple scanners being used simultaneously

from bc3_logging import getLogger
from logging import DEBUG, INFO, WARNING, ERROR, CRITICAL

# Operators
ENOT = 1 # ><
CALL = 2 # @
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
EXP = 17 # **
# MISSING NOT -> USE TILDE
BURROW = 18 # ?
CAST = 19 # ::
PARAM = 20 # #
CALLEND = 21 # \\
TE = 22 # ::=
BACK = 23 # $
BACKQUOTE = 24 # `
APPEND = 25 # ^

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
# RAISE = 43 # flag (Shelved)
GLOBAL = 43 # glob
LOG = 44 # log (TBD)

# Arrows
GOARROW1 = 60 # ->
GOARROW2 = 61 # =>
RETARROW1 = 62 # <-
RETARROW2 = 63 # <=
TILDE = 64 # ~ ARROWSHAFT / NOT

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
PERIOD = 78 # .
RANGE = 79 # ..

# Types
# INT = 80 # int
# FLOAT = 81 # float
# STR = 82 # str
# BOOL = 83 # bool
# ARRAY = 84 # array
# LIST = 85 # list
# FUNC = 86 # func
# LABEL = 87 # label
NONE = 88 # null (TBD)

# Literals
NUMBER = 90 # integer number
DECIMAL = 91 # float number (TBD)
STRING = 92 # string
IDENT = 93 # identifier

# Utility
LINEEND = 97 # ;
NEWLINE = 98 # \n
EOF = 99 # end of file marker

# Symbol sets
ARROWS = (GOARROW1, GOARROW2, RETARROW1, RETARROW2)
# TYPES = (INT, FLOAT, STR, BOOL)

FIRST_LABEL = set({TILDE, GOARROW1, GOARROW2, RETARROW1, RETARROW2, IDENT})
LAST_LABEL  = FIRST_LABEL

# FIRST_TYPE = set({INT, FLOAT, STR, BOOL, FUNC, LABEL, LIST})
# LAST_TYPE  = set({ARRAY}) | FIRST_TYPE

# FIRST_CAST = set({CAST})
# LAST_CAST  = LAST_TYPE

FIRST_LINEEND = set({LINEEND, NEWLINE})
LAST_LINEEND  = FIRST_LINEEND

FIRST_ATOM = set({NUMBER, DECIMAL, IDENT, STRING, LPAREN, LCURLY, BACKQUOTE, CALL})
LAST_ATOM  = set({NUMBER, DECIMAL, IDENT, STRING, RPAREN, RCURLY, BACKQUOTE, CALLEND, BURROW})

FIRST_INDEXED = FIRST_ATOM
LAST_INDEXED  = set({RBRAK}) | LAST_ATOM

FIRST_ELEMENT = FIRST_INDEXED
LAST_ELEMENT  = LAST_INDEXED

FIRST_UN_EXPR = set({PLUS, MINUS, TILDE}) | FIRST_ELEMENT
LAST_UN_EXPR  = LAST_ELEMENT

FIRST_EXP_EXPR = FIRST_UN_EXPR
LAST_EXP_EXPR  = LAST_UN_EXPR

FIRST_MULT_EXPR = FIRST_EXP_EXPR
LAST_MULT_EXPR  = LAST_EXP_EXPR

FIRST_ADD_EXPR = FIRST_MULT_EXPR
LAST_ADD_EXPR  = LAST_MULT_EXPR

FIRST_CMP_EXPR = FIRST_ADD_EXPR
LAST_CMP_EXPR  = LAST_ADD_EXPR

FIRST_EQ_EXPR = FIRST_CMP_EXPR
LAST_EQ_EXPR  = LAST_CMP_EXPR

FIRST_DIS_EXPR = FIRST_EQ_EXPR
LAST_DIS_EXPR  = LAST_EQ_EXPR

FIRST_CJN_EXPR = FIRST_DIS_EXPR
LAST_CJN_EXPR  = LAST_DIS_EXPR

FIRST_ENT_EXPR = FIRST_CJN_EXPR
LAST_ENT_EXPR  = LAST_CJN_EXPR

FIRST_EXPR = set({ENOT}) | FIRST_ENT_EXPR
LAST_EXPR  = LAST_ENT_EXPR

FIRST_INDEX = set({APPEND, BACK}) | FIRST_EXPR
LAST_INDEX = set({BACK}) | LAST_EXPR

FIRST_STMT = set({VAR, CONST, GLOBAL, READ, SET, DEL, GOTO, IF, TRY, EXEC, PRINT, INCLUDE, QUIT, RETURN, LOG})
LAST_STMT  = set({QUIT, RETURN, IDENT}) | LAST_EXPR | LAST_LABEL

FIRST_LINE = set({GOARROW1, GOARROW2, RETARROW1, RETARROW2, IDENT}) | FIRST_LINEEND | FIRST_STMT
LAST_LINE  = set({GOARROW1, GOARROW2, RETARROW1, RETARROW2, COLON}) | FIRST_LINEEND | LAST_LINEEND

FIRST_PROG = FIRST_LINE
LAST_PROG  = FIRST_PROG

FOLLOW_LINE = FIRST_LINE
FOLLOW_IDENT = FIRST_LINEEND
FOLLOW_STMT = FIRST_LINEEND
# FOLLOW_TYPE = set({LINEEND}) | FIRST_EXPR
FOLLOW_PROG = set({EOF})
FOLLOW_INDEX = set({RBRAK})

FOLLOW_EXPR = FIRST_LINEEND | FIRST_LABEL | FIRST_EXPR
FOLLOW_CJN_EXPR = FOLLOW_EXPR
FOLLOW_DIS_EXPR = set({OR, UNION}) | FOLLOW_CJN_EXPR
FOLLOW_EQ_EXPR = set({AND, INTER}) | FOLLOW_DIS_EXPR
FOLLOW_CMP_EXPR = set({EQ, NE, TE}) | FOLLOW_EQ_EXPR
FOLLOW_ADD_EXPR = set({LT, GT}) | FOLLOW_CMP_EXPR
FOLLOW_MULT_EXPR = set({PLUS, MINUS}) | FOLLOW_ADD_EXPR
FOLLOW_EXP_EXPR = set({MULT, DIV, INTDIV, MOD}) | FOLLOW_MULT_EXPR
FOLLOW_UN_EXPR = set({EXP}) | FOLLOW_EXP_EXPR
FOLLOW_ELEMENT = FOLLOW_UN_EXPR
FOLLOW_INDEXED = set({CAST}) | FOLLOW_ELEMENT
FOLLOW_ATOM = set({LBRAK}) | FOLLOW_INDEXED


STRONGSYMS = set({EOF, LINEEND, NEWLINE}) | FIRST_STMT
WEAKSYMS   = set({LINEEND, NEWLINE, COLON, CAST, RPAREN, RBRAK, RCURLY, BACKQUOTE, COMMA, TILDE})


KEYWORDS = {'var': VAR, 'const': CONST, 'in': READ, 'set': SET, 'del': DEL,
    'goto': GOTO, 'if': IF, 'try': TRY, 'cmp': EXEC,  'out': PRINT,
    'incl': INCLUDE, 'quit': QUIT, 'retn': RETURN, 'log': LOG, 'glob': GLOBAL}

# 'int': INT, 'float': FLOAT, 'bool': BOOL, 'str': STR,
# 'array': ARRAY, 'list': LIST, 'func': FUNC, 'label': LABEL, 'null': NONE,

# Used as a placeholder for those who need a scanner but will be assigned one later
class ScannerDummy:
    def __init__(self):
        self.logger = getLogger('dummy')
    def mark(self,msg,error,scanner):
        pass

class Scanner:
    def __init__(self,fname, src=None, log=True):
        # Initializes a scanner for new source code

        if log: self.logger = getLogger('scanner_{0}'.format(fname),fileLevel=DEBUG)
        else:   self.logger = getLogger('dummy')

        if src == None: self.src = open(fname).readlines()

        self.line, self.lastline, self.errline = 0, 0, 0 # current line, previous line, last error line
        self.pos, self.lastpos, self.errpos = 0, 0, 0 # current pos in line, previous position, last error position
        self.sym, self.val = None, None # current symbol, value associated with symbol
        self.source, self.index = src, 0 # raw code, index in line, current line index in source
        self.jump, self.newline, self.fname = False, 0, fname # jump on new line, line to jump to, file name
        self.error, self.suppress = False, False # error detected, supress detected errors
        self.getChar(); self.getSym() # Load initial character and get symbol

    def reset(self):
        global logger
        # Reinitializes scanner for current source
        self.line, self.lastline, self.errline = 0, 0, 0
        self.pos, self.lastpos, self.errpos = 0, 0, 0
        self.sym, self.val = None, None
        self.index = 0
        self.jump, self.newline = False, 0
        self.error, self.suppress = False, False
        self.getChar(); self.getSym()

        self.logger.info('reset scanner')

    def resetLine(self, setline):
        # Resets all parsing variables to be at the beginning of a specified line
        self.line, self.lastline, self.errline = setline, setline-1, setline-1
        self.pos, self.lastpos, self.errpos = 0, 0, 0
        self.sym, self.val = None, None
        self.index = 0
        self.jump, self.newline = False, 0

        # TODO FIX ERROR: works as expected?
        for i,src_line in enumerate(self.source.splitlines()):
            if i == self.newline: break
            else: self.index += len(src_line)+1 # Include newline

        self.logger.debug('reset to line {0} pos {0} index {1}'.format(setline, self.pos,self.index))

    def lineInfo(self):
        return 'line {0} pos {1}'.format(self.lastline+1,self.lastpos)

    def mark(self, msg=None, level='error'):
        # Marks an error and sets error flag to true
        if level in set({'error','critical'}):
            self.setError()

        if not self.suppress and msg != None:
            if self.lastline > self.errline or self.lastpos > self.errpos:
                # print('file',self.fname,level,': line', self.lastline+1, 'pos', self.lastpos, msg)

                if level == 'debug':    self.logger.debug('{0} {1}'.format(self.lineInfo(),msg))
                elif level == 'info':   self.logger.info('{0} {1}'.format(self.lineInfo(),msg))
                elif level == 'warning':self.logger.warning('{0} {1}'.format(self.lineInfo(),msg))
                elif level == 'error':  self.logger.error('{0} {1}'.format(self.lineInfo(),msg))

            if level == 'critical':     self.logger.critical('{0} {1}'.format(self.lineInfo(),msg))

            self.errline, self.errpos = self.lastline, self.lastpos

    def setError(self,level=True):
        self.error = level

    def setGoto(self, line):
        # Sets a specific line to jump to when the current line is fully parsed
        self.jump, self.newline = True, line

        self.logger.info('set jump to {0}'.format(self.newline))

    def execGoto(self):
        # Executes the line jump
        self.logger.info('execute jump')

        self.resetLine(self.newline)
        self.getChar(); self.getSym()

    def number(self):
        # Parses a number to a integer or float
        self.sym, self.val, div = NUMBER, 0, 10
        while '0' <= self.ch <= '9':
            self.val = 10 * self.val + int(self.ch)
            self.getChar()
        if self.ch == '.':
            self.getChar()
            self.sym = DECIMAL
            while '0' <= self.ch <= '9':
                self.val =  self.val + int(self.ch) / div
                self.getChar(); div /= 10

        if self.ch == 'f':
            self.getChar()
            self.sym = DECIMAL

        if self.val >= 2**31:
            self.mark('number too large, got {0}'.format(self.val),'warning')
        elif self.val <= -2**-31:
            self.mark('number too small, got {0}'.format(self.val),'warning')

    def string(self, open):
        # Parses a string
        self.getChar()
        start = self.index - 1
        while chr(0) != self.ch != open: # TODO: break at newline too
            if self.ch == '\\':
                if False:   pass # placeholder for escaped chars
                else:       self.getChar() # Use \ to escape open
            self.getChar()
        if self.ch == chr(0): self.mark('string not terminated'); self.sym = None;
        else:
            self.sym = STRING
            self.val = self.source[start:self.index-1]
            self.getChar(); # Get rid of ending quote

    def identKW(self):
        # Parses a word as either a keyword or identifier
        start = self.index - 1
        while ('A' <= self.ch <= 'Z') or ('a' <= self.ch <= 'z') or ('0' <= self.ch <= '9') or (self.ch == '_'): self.getChar()
        self.val = self.source[start:self.index-1]

        if self.val in set({'print','output'}):
            self.mark('output is \'out\'','warning'); self.sym = PRINT
        elif self.val in set({'read'}):
            self.mark('input is \'in\'','warning'); self.sym = PRINT
        else:
            self.sym = KEYWORDS[self.val] if self.val in KEYWORDS else IDENT

    def blockcomment(self):
        # Keeps taking inputs until the end comment marker is found
        start = self.line
        while chr(0) != self.ch:
            if self.ch == '*':
                self.getChar()
                if self.ch == '/':
                     self.getChar(); break
            else:
                self.getChar()
        if self.ch == chr(0): self.mark('comment not terminated')
        else: self.getChar()

        self.logger.debug('block comment from line {0} to {1}'.format(start,self.line))

    def linecomment(self):
        # Keeps taking inputs until a newline or EOF is found
        # logger.debug('found line comment')
        self.logger.debug('line comment started line {0}'.format(self.line))
        while chr(0) != self.ch != '\n': self.getChar()

    def getChar(self):
        # Retrieves the next character in the input (does not consume input)
        # Jumps lines as required
        if self.index == len(self.source): self.ch = chr(0)
        else:
            self.ch, self.index = self.source[self.index], self.index + 1
            self.lastpos = self.pos
            if self.ch == '\n':
                self.pos, self.line = 0, self.line + 1
            else:
                self.lastline, self.pos = self.line, self.pos + 1
            # if self.ch != '\n':


    def getSym(self):
        # Determines the next symbol in the input

        while chr(0) < self.ch <= ' ' and self.ch != '\n':
            self.getChar()

        s = self.index # start of token parse

        if 'A' <= self.ch <= 'Z' or 'a' <= self.ch <= 'z' or self.ch == '_': self.identKW()
        elif self.ch == "'" or self.ch == '"': self.string(self.ch)
        elif '0' <= self.ch <= '9': self.number()

        elif self.ch == '>':
            self.getChar()
            if self.ch == '<': self.getChar(); self.sym = ENOT
            else: self.sym = GT
        elif self.ch == '@': self.getChar(); self.sym = CALL
        elif self.ch == '#': self.getChar(); self.sym = PARAM
        elif self.ch == '|':
            self.getChar()
            if self.ch == '|': self.getChar(); self.sym = UNION
            else: self.sym = OR
        elif self.ch == '&':
            self.getChar()
            if self.ch == '&': self.getChar(); self.sym = INTER
            else: self.sym = AND
        elif self.ch == '=':
            self.getChar()
            if self.ch == '>': self.getChar(); self.sym = GOARROW2
            else: self.sym = EQ
        elif self.ch == '<':
            self.getChar()
            if self.ch == '-': self.getChar(); self.sym = RETARROW1
            elif self.ch == '=': self.getChar(); self.sym = RETARROW2
            elif self.ch == '>': self.getChar(); self.sym = NE
            else: self.sym = LT
        elif self.ch == '+': self.getChar(); self.sym = PLUS
        elif self.ch == '-':
            self.getChar()
            if self.ch == '>': self.getChar(); self.sym = GOARROW1
            else: self.sym = MINUS
        elif self.ch == '*':
            self.getChar();
            if self.ch == '*': self.getChar(); self.sym = EXP
            else: self.sym = MULT
        elif self.ch == '/':
            self.getChar();
            if self.ch == '/': self.getChar(); self.linecomment(); self.getSym()
            elif self.ch == '*': self.getChar(); self.blockcomment(); self.getSym()
            else: self.sym = DIV
        elif self.ch == '\\':
            self.getChar();
            if self.ch == '\\': self.getChar(); self.sym = CALLEND
            else: self.sym = INTDIV
        elif self.ch == '%': self.getChar(); self.sym = MOD
        elif self.ch == '$': self.getChar(); self.sym = BACK
        elif self.ch == '`': self.getChar(); self.sym = BACKQUOTE
        # elif self.ch == '!': self.getChar(); self.sym = NOT
        elif self.ch == ':':
            self.getChar();
            if self.ch == ':':
                self.getChar();
                if self.ch == '=': self.getChar(); self.sym = TE
                else: self.sym = CAST
            else: self.sym = COLON
        elif self.ch == '.':
            self.getChar();
            if self.ch == '.': self.getChar(); self.sym = RANGE
            else: self.sym = PERIOD
        elif self.ch == '~': self.getChar(); self.sym = TILDE
        elif self.ch == '^': self.getChar(); self.sym = APPEND
        elif self.ch == '?': self.getChar(); self.sym = BURROW
        elif self.ch == '(': self.getChar(); self.sym = LPAREN
        elif self.ch == ')': self.getChar(); self.sym = RPAREN
        elif self.ch == '[': self.getChar(); self.sym = LBRAK
        elif self.ch == ']': self.getChar(); self.sym = RBRAK
        elif self.ch == '{': self.getChar(); self.sym = LCURLY
        elif self.ch == '}': self.getChar(); self.sym = RCURLY
        elif self.ch == ',': self.getChar(); self.sym = COMMA
        elif self.ch == ';': self.getChar(); self.sym = LINEEND
        elif self.ch == '\n': self.getChar(); self.sym = NEWLINE
        elif self.ch == chr(0): self.sym = EOF
        else: self.mark('illegal character, got {0}'.format(self.ch)); self.getChar(); self.sym = None

        e = self.index # end of token parse

        if self.sym != NEWLINE:
            self.logger.debug('parsed {0} as {1}'.format(self.source[s-1:e-1],self.sym))
