# NGL Bytecode 3.0 Scanner
# Designed so that there can be multiple scanners being used simultaneously

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

# Symbol sets
ARROWS = (GOARROW1, GOARROW2, RETARROW1, RETARROW2)

KEYWORDS = {'int': INT, 'float': FLOAT, 'bool': BOOL, 'str': STR,
    'array': ARRAY, 'list': LIST, 'null': NONE, 'var': VAR, 'const': CONST,
    'in': READ, 'set': SET, 'del': DEL, 'goto': GOTO, 'if': IF, 'try': TRY,
    'cmp': EXEC,  'out': PRINT, 'incl': INCLUDE, 'quit': QUIT, 'retn': RETURN,
    'flag': RAISE, 'log': LOG}

# Used as a placeholder for those who need a scanner but will be assigned one later
class ScannerDummy:
    def __init__(self):
        pass
    def mark(self,msg):
        pass

class Scanner:
    def __init__(self,fname, src=None, log=False):
        global logger
        # Initializes a scanner for new source code

        if src == None: self.src = open(fname).readlines()

        self.line, self.lastline, self.errline = 0, 0, 0 # current line, previous line, last error line
        self.pos, self.lastpos, self.errpos = 0, 0, 0 # current pos in line, previous position, last error position
        self.sym, self.val = None, None # current symbol, value associated with symbol
        self.source, self.index = src, 0 # raw code, index in line, current line index in source
        self.jump, self.newline, self.fname = False, 0, fname # jump on new line, line to jump to, file name
        self.error, self.suppress = False, False # error detected, supress detected errors
        self.getChar(); self.getSym() # Load initial character and get symbol

        # logger = logging.getLogger('scanner')
        # if log:         self.initLogging()

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

    def resetLine(self, setline):
        # Resets all parsing variables to be at the beginning of a specified line
        self.line, self.lastline, self.errline = setline, setline, setline
        self.pos, self.lastpos, self.errpos = 0, 0, 0
        self.sym, self.val = None, None
        self.index = 0
        self.jump, self.newline = False, 0

    def mark(self, msg):
        # Marks an error and sets error flag to true
        self.error = True
        if not self.suppress:
            if self.lastline > self.errline or self.lastpos > self.errpos:
                print('file',self.fname,'error: line', self.lastline+1, 'pos', self.lastpos, msg)
            self.errline, self.errpos = self.lastline, self.lastpos

    def setGoto(self, line):
        # Sets a specific line to jump to when the current line is fully parsed
        self.jump, self.newline = True, line

    def execGoto(self):
        # Executes the line jump
        resetline(self.newline)

        # FIX: may be broken
        for i,src_line in enumerate(self.source.splitlines()):
            if i == newline: break
            else: self.index += len(src_line)+1 # Include newline

        self.getChar(); self.getSym()

    def nextLine(self):
        # Jumps to the next source line
        # Executed after an accepted parse of LINEEND
        self.pos, self.line = 0, self.line + 1

    def number(self):
        global logger
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

        # logger.debug('parsed number %s' % self.val)
        if self.val >= 2**31:
            self.mark('number too large'); self.val = 0
        elif self.val <= 2**-31:
            self.mark('number too small'); self.val = 0

    # Parses a string
    def string(self, open):
        global logger
        self.getChar()
        start = self.index - 1
        while chr(0) != self.ch != open: self.getChar()
        if self.ch == chr(0): mark('string not terminated'); self.sym = None;
        else:
            self.sym = STRING; self.val = self.source[start:self.index-1]
            self.getChar(); # Get rid of ending '

            # logger.debug('parsed string %s' % self.val)

    def identKW(self):
        global logger
        # Parses a word as either a keyword or identifier
        start = self.index - 1
        while ('A' <= self.ch <= 'Z') or ('a' <= self.ch <= 'z') or ('0' <= self.ch <= '9') or (self.ch == '_'): self.getChar()
        self.val = self.source[start:self.index-1]
        self.sym = KEYWORDS[self.val] if self.val in KEYWORDS else IDENT

        # logger.debug('parsed %s as %s' % (self.val,self.sym))

    def blockcomment(self):
        global logger
        # Keeps taking inputs until the end comment marker is found
        # logger.debug('found block comment')
        while chr(0) != self.ch:
            if self.ch == '*':
                self.getChar()
                if self.ch == '/':
                     self.getChar(); break
            else:
                self.getChar()
        if self.ch == chr(0): mark('comment not terminated')
        else: self.getChar()

    def linecomment(self):
        global logger
        # Keeps taking inputs until a newline or EOF is found
        # logger.debug('found line comment')
        while chr(0) != self.ch != '\n': self.getChar()


    def getChar(self):
        # Retrieves the next character in the input (does not consume input)
        # Jumps lines as required
        if self.index == len(self.source): self.ch = chr(0)
        else:
            self.ch, self.index = self.source[self.index], self.index + 1
            self.lastpos = self.pos
            # if ch == '\n':
            #     pos, line = 0, line + 1
            # else:
            self.lastline, self.pos = self.line, self.pos + 1


    def getSym(self):
        # Determines the next symbol in the input
        global logger, sym, jump, source

        while chr(0) < self.ch <= ' ' and self.ch != '\n':
            self.getChar()

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
        elif self.ch == '\n': self.getChar(); self.sym = LINEEND
        elif self.ch == chr(0): self.sym = EOF
        else: self.mark('illegal character: %s' % self.ch); self.getChar(); self.sym = None