# NGL Bytecode 2.1 Scanner

from copy import deepcopy

PLUS = 1; # +
MINUS = 2; # -
MULT = 3; # *
DIV = 4; # /
MOD = 5; # %
EXP = 6; # ^
AND = 6; # &
OR = 7; # |
NOT = 8; # !
E_NOT = 9; # ><
EQ = 10; # =
NE = 11; # <>
LT = 12; # <
GT = 13; # >
GOARROW1 = 14; # ->
GOARROW2 = 15; # =>
RETARROW1 = 16; # <-
RETARROW2 = 17; # <=
ARROW_SHAFT = 18; # ~
NOJUMP = 19; # .
COMMA = 20; # ,
COLON = 21; # :
CAST = 22; # ::
SEMICOLON = 23; # ;
PARAM = 24; # @
LPAREN = 25; # (
RPAREN = 26; # )
LBRAK = 27; # [
RBRAK = 28; # ]
LCURLY = 29; # {
RCURLY = 30; # }

INT = 31; # int
FLOAT = 32; # float
BOOL = 33; # bool
STRING = 34; # str
ARRAY = 35; # array
LIST = 36; # list
NULL = 37; # null

NUMBER = 38; # `val` holds corresponding number
RAW_STRING = 39; # `val` holds string contents
BOOLEAN = 40; # `val` holds true or false
IDENT = 41; # `val` holds string identifier
ARG = 42; # `val` holds the exact argument

VAR = 50; # var
SET = 51; # set
GOTO = 52; # goto
IF = 53; # if
COMPARE = 54; # exec, formerly: cmp
PRINT = 55; # print
READ = 56; # read
DELETE = 57; # del
TRY = 58; # try
INCLUDE = 59; # incl
RETURN = 60; # ret
QUIT = 61; # quit

USRFUNC = 80; # User functions
TYPE = 81; # typ
LABEL = 82; # lab
LEN = 83; # len

EOF = 99;

PRIMATIVE = {INT, FLOAT, BOOL, STRING, NULL}
COLLECTION = {ARRAY, LIST}
ARROWS = {GOARROW1, GOARROW2, RETARROW1, RETARROW2}

# Keywords in the language
KEYWORDS = {'int': INT, 'float': FLOAT, 'bool': BOOL, 'str': STRING,
    'array': ARRAY, 'list': LIST, 'null': NULL, 'var': VAR, 'set': SET,
    'goto': GOTO, 'if': IF, 'exec': COMPARE, 'print': PRINT, 'read': READ,
    'del': DELETE,  'try': TRY, 'len': LEN, 'typ': TYPE, 'lab': LABEL,
    'true': BOOLEAN, 'false': BOOLEAN, 'ret': RETURN, 'incl': INCLUDE,
    'quit': QUIT}
    # 'arg0': ARG, 'arg1': ARG, 'arg2': ARG, 'arg3': ARG, 'arg4': ARG,
    # 'arg5': ARG, 'arg6': ARG, 'arg7': ARG, 'arg8': ARG, 'arg9': ARG}

class ScannerState: # For saving and loading the state of the scanner
    def __init__(self, *args):
        # for i in range(len(args)): print(i,args[i])
        # print()

        self.line, self.lastline, self.errline = args[0], args[1], args[2]
        self.pos, self.lastpos, self.errpos = args[3], args[4], args[5]
        self.sym, self.val, self.error = args[6], args[7], args[8]
        self.index, self.jump, self.newline = args[9], args[10], args[11]
        self.suppress, self.source, self.filename = args[12], args[13], args[14]
        self.ch = args[15]

def init(file : str, src : str) -> None:
    # Initializes scanner for new source code
    global line, lastline, errline, pos, lastpos, errpos, filename
    global sym, val, error, source, index, jump, newline, suppress
    line, lastline, errline = 0, 0, 0
    pos, lastpos, errpos = 0, 0, 0
    sym, val, error, source, index = None, None, False, src, 0
    jump, newline, suppress, filename = False, 0, False, file
    getChar(); getSym()

def reset():
    global line, lastline, errline, pos, lastpos, errpos
    global sym, val, error, index, jump, newline, suppress
    # Reinitializes scanner for current source
    line, lastline, errline = 0, 0, 0
    pos, lastpos, errpos = 0, 0, 0
    sym, val, error, index = 0, 0, False, 0
    jump, newline, suppress = False, 0, False
    getChar(); getSym()

def save():
    global line, lastline, errline, pos, lastpos, errpos, filename
    global sym, val, error, source, index, jump, newline, suppress, ch
    return ScannerState(line,lastline,errline,pos,lastpos,errpos,sym,val,error,index,jump,newline,suppress,source,filename,ch)

def load(state):
    global line, lastline, errline, pos, lastpos, errpos, filename
    global sym, val, error, source, index, jump, newline, suppress, ch
    line, lastline, errline = state.line, state.lastline, state.errline
    pos, lastpos, errpos = state.pos, state.lastpos, state.errpos
    sym, val, error = state.sym, state.val, state.error
    index, jump, newline = state.index, state.jump, state.newline
    suppress, source, filename = state.suppress, state.source, state.filename
    ch = state.ch

# Sets a specific line to jump to when the current line is fully parsed
def set_goto(n_line : int) -> None:
    global jump, newline
    jump, newline = True, n_line

# Executes the line jump
def exec_goto() -> None:
    global line, lastline, errline, pos, lastpos, errpos
    global sym, val, index, jump, newline, source
    line, lastline, errline = newline, newline, newline # lastline gets updated by getChar
    pos, lastpos, errpos = 0, 0, 0
    sym, val, jump, index = None, None, False, 0

    index = 0
    for i,src_line in enumerate(source.splitlines()):
        if i == newline: break
        else: index += len(src_line)+1 # Include newline

    getChar(); getSym()

# Retrieves the next character in the input
def getChar( wte = False):
    global line, lastline, pos, lastpos, ch, index
    if index == len(source): ch = chr(0)
    else:
        ch, index = source[index], index + 1
        lastpos = pos
        if ch == '\n':
            pos, line = 0, line + 1
        else:
            lastline, pos = line, pos + 1

# Marks an error and sets error flag to true
def mark(msg):
    global errline, errpos, error, suppress, filename
    error = True
    if not suppress:
        if lastline > errline or lastpos > errpos:
            print('file',filename,'error: line', lastline+1, 'pos', lastpos, msg)
        errline, errpos = lastline, lastpos

# Parses a integer of floating point number
def number():
    global sym, val
    sym, val, frac, div = NUMBER, 0, 0, 10
    while '0' <= ch <= '9':
        val = 10 * val + int(ch)
        getChar()
    if ch == '.':
        getChar()
        while '0' <= ch <= '9':
            value =  value + int(ch) / div
            getChar(); div /= 10

    if val >= 2**31:
        mark('number too large'); val = 0

def raw_string(open : str):
    global sym, val
    getChar()
    start = index - 1
    while chr(0) != ch != open: getChar()
    if ch == chr(0): mark('string not terminated'); sym = None;
    else:
        sym = RAW_STRING; val = source[start:index-1]
        getChar(); # Get rid of terminating '

def identKW():
    global sym, val
    start = index - 1
    while ('A' <= ch <= 'Z') or ('a' <= ch <= 'z') or ('0' <= ch <= '9') or (ch == '_'): getChar()
    val = source[start:index-1]
    sym = KEYWORDS[val] if val in KEYWORDS else IDENT # (USRFUNC if val in usrfunc else IDENT)

# Keeps taking inputs until the end comment marker is found
def blockcomment():
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
    while chr(0) != ch != '\n': getChar()

# Determines the next symbol in the input
def getSym():
    global sym, jump, source

    while chr(0) < ch <= ' ':
        if jump and ch == '\n':
            exec_goto() # Will call getSym()
            return
        else:
            getChar()

    if 'A' <= ch <= 'Z' or 'a' <= ch <= 'z' or ch == '_': identKW()
    elif ch == "'" or ch == '"': raw_string(ch)
    elif '0' <= ch <= '9': number()

    elif ch == '+': getChar(); sym = PLUS
    elif ch == '*': getChar(); sym = MULT
    elif ch == '/':
        getChar();
        if ch == '/': getChar(); linecomment(); getSym()
        if ch == '*': getChar(); blockcomment(); getSym()
        else: sym = DIV
    elif ch == '%': getChar(); sym = MOD
    elif ch == '^': getChar(); sym = EXP
    elif ch == '&': getChar(); sym = AND
    elif ch == '|': getChar(); sym = OR
    elif ch == '!': getChar(); sym = NOT
    elif ch == '=':
        getChar();
        if ch == '>': getChar(); sym = GOARROW2
        else: sym = EQ
    elif ch == '-':
        getChar();
        if ch == '>': getChar(); sym = GOARROW1
        else: sym = MINUS
    elif ch == '<':
        getChar();
        if ch == '-': getChar(); sym = RETARROW1
        elif ch == '=': getChar(); sym = RETARROW2
        elif ch == '>': getChar(); sym = NE
        else: sym = LT
    elif ch == '>':
        getChar();
        if ch == '<': getChar(); sym = E_NOT
        else: sym = GT
    elif ch == '~': getChar(); sym = ARROW_SHAFT
    elif ch == ';': getChar(); sym = SEMICOLON
    elif ch == ',': getChar(); sym = COMMA
    elif ch == ':':
        getChar();
        if ch == ':': getChar(); sym = CAST
        else: sym = COLON
    elif ch == '.': getChar(); sym = NOJUMP
    elif ch == '(': getChar(); sym = LPAREN
    elif ch == ')': getChar(); sym = RPAREN
    elif ch == '[': getChar(); sym = LBRAK
    elif ch == ']': getChar(); sym = RBRAK
    elif ch == '{': getChar(); sym = LCURLY
    elif ch == '}': getChar(); sym = RCURLY
    elif ch == '@': getChar(); sym = PARAM
    elif ch == chr(0): sym = EOF
    else: mark('illegal character: '+ch); getChar(); sym = None


if __name__ == '__main__':
    fname = 'test'
    src = '''
var i:int 23;
goto jeb ->;
bag: set i '4'::int;
<- print 'yay';
'''
    init(fname,src)
    mark('phooey')
