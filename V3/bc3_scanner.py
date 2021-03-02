# NGL Bytecode 3.0 Scanner
# Designed so that there can be multiple scanners being used simultaneously

from bc3_logging import getLogger

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
# RAISE = 43 # flag (Shelved)
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

# Types
INT = 80 # int
FLOAT = 81 # float
STR = 82 # str
BOOL = 83 # bool
ARRAY = 84 # array
LIST = 85 # list
FUNC = 86 # func
LABEL = 87 # label
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
TYPES = (INT, FLOAT, STR, BOOL)

FIRST_LABEL = set({ARROWSHAFT, GOARROW1, GOARROW2, RETARROW1, RETARROW2, NOJUMP, IDENT})
LAST_LABEL  = FIRST_LABEL

FIRST_TYPE = set({INT, FLOAT, STR, BOOL, FUNC, LABEL, LIST})
LAST_TYPE  = set({ARRAY}) | FIRST_TYPE

FIRST_CAST = set({CAST})
LAST_CAST  = LAST_TYPE

FIRST_LINEEND = set({LINEEND, NEWLINE})
LAST_LINEEND  = FIRST_LINEEND

FIRST_ATOM = set({NUMBER, DECIMAL, IDENT, STRING, LPAREN, LCURLY, LBRAK})
LAST_ATOM  = set({NUMBER, DECIMAL, IDENT, STRING, RPAREN, RCURLY, LBRAK})

FIRST_SUBATOM = FIRST_ATOM
LAST_SUBATOM  = set({RBRAK}) | LAST_ATOM

FIRST_EXPR_L9 = FIRST_SUBATOM
LAST_EXPR_L9  = LAST_CAST | LAST_SUBATOM

FIRST_EXPR_L8 = set({PLUS, MINUS, NOT}) | FIRST_EXPR_L9
LAST_EXPR_L8  = LAST_EXPR_L9

FIRST_EXPR_L7 = FIRST_EXPR_L8
LAST_EXPR_L7  = LAST_EXPR_L8

FIRST_EXPR_L6 = FIRST_EXPR_L8
LAST_EXPR_L6  = LAST_EXPR_L8

FIRST_EXPR_L5 = FIRST_EXPR_L6
LAST_EXPR_L5  = LAST_EXPR_L6

FIRST_EXPR_L4 = FIRST_EXPR_L5
LAST_EXPR_L4  = LAST_EXPR_L5

FIRST_EXPR_L3 = FIRST_EXPR_L4
LAST_EXPR_L3  = LAST_EXPR_L4

FIRST_EXPR_L2 = FIRST_EXPR_L3
LAST_EXPR_L2  = LAST_EXPR_L3

FIRST_EXPR_S2 = FIRST_EXPR_L2
LAST_EXPR_S2  = LAST_EXPR_L2

FIRST_EXPR_L1 = FIRST_EXPR_S2
LAST_EXPR_L1  = LAST_EXPR_S2

FIRST_EXPR_S1 = FIRST_EXPR_L1
LAST_EXPR_S1  = LAST_EXPR_L1

FIRST_EXPR_L0 = FIRST_EXPR_L1
LAST_EXPR_L0  = LAST_EXPR_L1

FIRST_EXPR = set({ENOT}) | FIRST_EXPR_L0
LAST_EXPR  = LAST_EXPR_L0

FIRST_STMT = set({VAR, CONST, READ, SET, DEL, GOTO, IF, TRY, EXEC, PRINT, INCLUDE, QUIT, RETURN, LOG})
LAST_STMT  = set({QUIT, RETURN, IDENT}) | LAST_CAST | LAST_EXPR | LAST_LABEL

FIRST_LINE = set({GOARROW1, GOARROW2, RETARROW1, RETARROW2, IDENT}) | FIRST_LINEEND | FIRST_STMT
LAST_LINE  = set({GOARROW1, GOARROW2, RETARROW1, RETARROW2, COLON}) | FIRST_LINEEND | LAST_LINEEND

FIRST_PROG = FIRST_LINE
LAST_PROG  = FIRST_PROG

STRONGSYMS = set({LINEEND, NEWLINE}) | FIRST_STMT
WEAKSYMS   = set({LINEEND, NEWLINE})


KEYWORDS = {'int': INT, 'float': FLOAT, 'bool': BOOL, 'str': STR,
    'array': ARRAY, 'list': LIST, 'func': FUNC, 'label': LABEL, 'null': NONE,
    'var': VAR, 'const': CONST, 'in': READ, 'set': SET, 'del': DEL,
    'goto': GOTO, 'if': IF, 'try': TRY, 'cmp': EXEC,  'out': PRINT,
    'incl': INCLUDE, 'quit': QUIT, 'retn': RETURN, 'log': LOG}

# Used as a placeholder for those who need a scanner but will be assigned one later
class ScannerDummy:
    def __init__(self):
        self.logger = getLogger('dummy')
    def mark(self,msg,error,scanner):
        pass

class Scanner:
    def __init__(self,fname, src=None, log=True):
        # Initializes a scanner for new source code

        if log: self.logger = getLogger('scanner_{0}'.format(fname))
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

    def mark(self, msg=None, level='error'):
        # Marks an error and sets error flag to true
        if level in set({'error','critical'}):
            self.error = True

        if not self.suppress and msg != None:
            if self.lastline > self.errline or self.lastpos > self.errpos:
                # print('file',self.fname,level,': line', self.lastline+1, 'pos', self.lastpos, msg)

                if level == 'debug':    self.logger.debug('line {0} pos {1} {2}'.format(self.lastline+1,self.lastpos,msg))
                elif level == 'info':   self.logger.info('line {0} pos {1} {2}'.format(self.lastline+1,self.lastpos,msg))
                elif level == 'warning':self.logger.warning('line {0} pos {1} {2}'.format(self.lastline+1,self.lastpos,msg))
                elif level == 'error':  self.logger.error('line {0} pos {1} {2}'.format(self.lastline+1,self.lastpos,msg))

            if level == 'critical':     self.logger.critical('line {0} pos {1} {2}'.format(self.lastline+1,self.lastpos,msg))

            self.errline, self.errpos = self.lastline, self.lastpos

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
        if self.ch == chr(0): mark('string not terminated'); self.sym = None;
        else:
            self.sym = STRING
            self.val = self.source[start:self.index-1]
            self.getChar(); # Get rid of ending quote

    def identKW(self):
        # Parses a word as either a keyword or identifier
        start = self.index - 1
        while ('A' <= self.ch <= 'Z') or ('a' <= self.ch <= 'z') or ('0' <= self.ch <= '9') or (self.ch == '_'): self.getChar()
        self.val = self.source[start:self.index-1]
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
        if self.ch == chr(0): mark('comment not terminated')
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
        elif self.ch == '@': self.getChar(); self.sym = PARAM
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
        elif self.ch == '*': self.getChar(); self.sym = MULT
        elif self.ch == '/':
            self.getChar();
            if self.ch == '/': self.getChar(); self.linecomment(); self.getSym()
            elif self.ch == '*': self.getChar(); self.blockcomment(); self.getSym()
            else: self.sym = DIV
        elif self.ch == '\\': self.getChar(); self.sym = INTDIV
        elif self.ch == '%': self.getChar(); self.sym = MOD
        elif self.ch == '^': self.getChar(); self.sym = EXP
        elif self.ch == '!': self.getChar(); self.sym = NOT
        elif self.ch == ':':
            self.getChar();
            if self.ch == ':': self.getChar(); self.sym = CAST
            else: self.sym = COLON
        elif self.ch == '~': self.getChar(); self.sym = ARROWSHAFT
        elif self.ch == '.': self.getChar(); self.sym = NOJUMP
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
        else: self.mark('illegal character: %s' % self.ch); self.getChar(); self.sym = None

        e = self.index # end of token parse

        if self.sym != NEWLINE:
            self.logger.debug('parsed {0} as {1}'.format(self.source[s-1:e-1],self.sym))
