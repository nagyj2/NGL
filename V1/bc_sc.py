# ngl bytecode scanner'

ADD = 1; SUB = 2; MULT = 3; DIV = 4; MOD = 5; EXP = 80
AND = 6; OR = 7; NOT = 8; LNOT = 81
EQ = 9; NE = 10; LT = 11; GT = 12; LE_RETARROW2 = 13; GE = 14;
LPAREN = 15; RPAREN = 16; LBRAK = 17; RBRAK = 18; LCURLY = 19; RCURLY = 20;
PERIOD = 21; COMMA = 22; COLON = 23; DOUBLE_COLON = 24; SEMICOLON = 25;
IDENT = 26; NUMBER = 27; FULL_STRING = 28; TRUE = 29; FALSE = 30; NULL = 31;
INT = 32; FLOAT = 33; BOOL = 34; STRING = 35; ARRAY = 36; LIST = 37;
GOARROW1 = 38; GOARROW1_SHAFT = 39; RETARROW1 = 40; GOARROW2 = 41; GOARROW2_SHAFT = 42;
PARAM = 43;
VAR = 50; ASSIGN = 51; GOTO = 52; PRINT = 53; READ = 54; DELETE = 55; IF = 56;
TRY = 57; COMPARE = 58; INCLUDE = 59;
LEN = 70; TYPE = 71; LABEL = 72;
EOF = 99

# Following variables determine the state of the scanner:
# - `(line, pos)` is the location of the current symbol in source
# - `(lastline, lastpos)` is used to more accurately report errors
# - `(errline, errpos)` is used to suppress multiple errors at the same location
# - `ch` is the current character
# - `sym` the current symbol
# - if `sym` is `NUMBER`, `val` is the value of the number
# - if `sym` is `IDENT`, `val` is the identifier string
# - `source` is the string with the source program
#
# The source is specified as a parameter to the procedure `init`:

def init(src):
    global line, lastline, errline, pos, lastpos, errpos
    global sym, val, error, source, index, jump, newline, supress
    line, lastline, errline = 0, 0, 0
    pos, lastpos, errpos = 0, 0, 0
    sym, val, error, source, index = None, None, False, src, 0
    jump, newline, supress = False, 0, False
    getChar(); getSym()

# Goes to a specific line in source and starts execution
def set_goto(n_line):
    global jump, newline
    jump, newline = True, n_line

def exec_goto():
    global line, lastline, errline, pos, lastpos, errpos
    global sym, val, index, jump, newline, source
    line, lastline, errline = newline, newline, newline # lastline gets updated by getChar
    pos, lastpos, errpos = 0, 0, 0
    sym, val = None, None

    index = 0
    for i,src_line in enumerate(source.splitlines()):
        if i == newline: break
        else: index += len(src_line)+1 # Include newline

    jump, newline = False, 0
    getChar(); getSym()

# Retrieves the next character in the input

def getChar():
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
    global errline, errpos, error, suppress
    error = True
    if not supress:
        if lastline > errline or lastpos > errpos:
            print('error: line', lastline, 'pos', lastpos, msg)
        errline, errpos = lastline, lastpos

# Loads a number into 'val'. Will overflow and cause error if the number is too high

def number():
    # TODO: Add float support
    global sym, val
    sym, val = NUMBER, 0
    while '0' <= ch <= '9':
        val = 10 * val + int(ch)
        getChar()
    if val >= 2**31:
        mark('number too large'); val = 0

# Keywords in the language
KEYWORDS = {'int': INT, 'float': FLOAT, 'bool': BOOL, 'str': STRING, 'array': ARRAY, 'list': LIST,
    'var': VAR, 'set': ASSIGN, 'goto': GOTO, 'print': PRINT, 'true': TRUE, 'false': FALSE, 'null': NULL,
    'read': READ, 'del': DELETE, 'if': IF, 'cmp': COMPARE, 'try': TRY, 'len': LEN, 'type': TYPE,
    'label': LABEL}

def identKW():
    global sym, val
    start = index - 1
    while ('A' <= ch <= 'Z') or ('a' <= ch <= 'z') or ('0' <= ch <= '9') or (ch == '_'): getChar()
    val = source[start:index-1]
    sym = KEYWORDS[val] if val in KEYWORDS else IDENT

def identString(open):
    global sym, val
    getChar()
    start = index - 1
    while chr(0) != ch != open: getChar()
    if ch == chr(0): mark('string not terminated'); sym = None;
    else:
        sym = FULL_STRING; val = source[start:index-1]
        getChar(); # Get rid of terminating '

def finishLine():
    global sym # For errors. Just finish the line
    while chr(0) != ch != ';': getChar()
    if ch == chr(0): sym = None;

# Keeps taking inputs until the end comment marker is found

def blockcomment():
    while chr(0) != ch != '}': getChar()
    if ch == chr(0): mark('comment not terminated')
    else: getChar()

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
    elif ch == "'" or ch == '"': identString(ch)
    elif '0' <= ch <= '9': number()
    elif ch == '/':
        getChar();
        if ch == '/': getChar(); linecomment(); getSym()
        else: sym = DIV
    elif ch == '*': getChar(); sym = MULT
    elif ch == '%': getChar(); sym = MOD
    elif ch == '+': getChar(); sym = ADD
    elif ch == '-':
        getChar();
        if ch == '>': getChar(); sym = GOARROW1
        elif ch == '-': sym = GOARROW1_SHAFT
        else: sym = SUB
    elif ch == '=':
        getChar();
        if ch == '>': getChar(); sym = GOARROW2
        elif ch == '=': sym = GOARROW2_SHAFT
        else: sym = EQ
    elif ch == '<':
        getChar()
        if ch == '=': getChar(); sym = LE_RETARROW2
        elif ch == '-': getChar(); sym = RETARROW1
        elif ch == '>': getChar(); sym = NE
        else: sym = LT
    elif ch == '>':
        getChar()
        if ch == '=': getChar(); sym = GE
        else: sym = GT
    elif ch == ';': getChar(); sym = SEMICOLON
    elif ch == ',': getChar(); sym = COMMA
    elif ch == ':':
        getChar()
        if ch == ':': getChar(); sym = DOUBLE_COLON
        else: sym = COLON
    elif ch == '.': getChar(); sym = PERIOD
    elif ch == '(': getChar(); sym = LPAREN
    elif ch == ')': getChar(); sym = RPAREN
    elif ch == '[': getChar(); sym = LBRAK
    elif ch == ']': getChar(); sym = RBRAK
    elif ch == '{': getChar(); sym = LCURLY
    elif ch == '}': getChar(); sym = RCURLY
    elif ch == '&': getChar(); sym = AND
    elif ch == '|': getChar(); sym = OR
    elif ch == '^': getChar(); sym = EXP
    elif ch == '~': getChar(); sym = NOT
    elif ch == '!': getChar(); sym = LNOT
    elif ch == '#': getChar(); sym = PARAM
    elif ch == chr(0): sym = EOF
    else: mark('illegal character'); print('>'+ch+'<'); getChar(); sym = None


if __name__ == '__main__':
    text = '''
    => var1 :: array :: int;
    '''.lstrip()

    init(text)

    while sym!=EOF:
        print(sym)
        getSym()
