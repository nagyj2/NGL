# NGL Speed Scanner

PLUS = 1; # +
MINUS = 2; # -
MULT = 3; # *
DIV = 4; # /
AND = 5; # /\
OR = 6; # \/
EQ = 7; # =
LT = 8; # <
GT = 9; # >
NOT = 10; # ~
INPUT = 11; # %
COLON = 12; # :
LINEEND = 13; # ;
LPAREN = 14; # (
RPAREN = 15; # )
LCURLY = 16; # {
RCURLY = 17; # }
BOOL = 18; # _
INPUT = 19 # .;  For parsing and AST nodes
COMMA = 20 # ,
MOD = 21 # %
GE = 22 # |>
LE = 23 # <|
NE = 24 # ?????

NUMBER = 30; # `val` holds corresponding number
RAW_STRING = 31; # `val` holds string contents
IDENT = 32; # `val` holds string identifier

INT = 33 # #
IDENTITY_INT = 34 # ##
FLOAT = 35 # %
IDENTITY_FLOAT = 36 # %%
STRING = 37 # @
IDENTITY_STRING = 38 # @@
BOOLEAN = 39 # ^
IDENTITY_BOOLEAN = 40 # ^^

IF = 50; # ?
ELSE = 51; # ~?
PRINT = 52; # !
LOOP = 53; # $
EXIT = 54; # \
FUNC_DEF = 55; # ![
FUNC_CALL = 56; # ?[
FUNC_END = 57; # ]

BLOCK = 80 # For AST nodes - indicates a sequence of statements
ASSIGN = 81 # For AST nodes - indicates a sequence of assignments
PARAM = 82 # AST Nodes - indicates a sequence of identifiers
RETURN = 83 # AST Nodes - / in a function definition
FUNC = 84 # AST Function type

EOF = 99

def dump_code():
    print(f'{source[:index-1]}∆{source[index:]}')

def init(file : str, src : str) -> None:
    # Initializes scanner for new source code
    global line, lastline, errline, pos, lastpos, errpos, filename
    global sym, val, error, source, index
    line, lastline, errline = 0, 0, 0
    pos, lastpos, errpos = 0, 0, 0
    sym, val, error = None, None, False
    source, index, filename = src, 0, file
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
    global errline, errpos, error, filename, sym
    error = True
    if lastline > errline or lastpos > errpos:
        print('file',filename,'error: line', lastline+1, 'pos', lastpos, msg,'<last sym',str(sym)+'>')
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
            val =  val + int(ch) / div
            getChar(); div /= 10

    if val >= 2**31:
        mark('number too large'); val = 0

def raw_string(open : str):
    global sym, val
    getChar()
    start = index - 1
    while chr(0) != ch != open: getChar()
    if ch == chr(0): mark('string not terminated'); sym = None
    else:
        sym = RAW_STRING; val = source[start:index-1]
        getChar(); # Get rid of terminating '

def multichar_var(open: str):
    global sym, val
    getChar()
    start = index - 1
    while chr(0) != ch != open: getChar()
    if ch == chr(0): mark('variable not terminated'); sym = None
    else:
        sym = IDENT; val = source[start:index-1]
        getChar(); # Get rid of terminating '

def ident():
    global sym, val
    val, sym = ch, IDENT
    getChar()

# Determines the next symbol in the input
def getSym():
    global sym, jump, source

    while chr(0) < ch <= ' ':
        getChar()

    if 'A' <= ch <= 'Z' or 'a' <= ch <= 'z': ident()
    elif '0' <= ch <= '9': number()
    elif ch == "'" or ch == '"': raw_string(ch)
    elif ch == '`': multichar_var('`')

    elif ch == '+': getChar(); sym = PLUS
    elif ch == '-': getChar(); sym = MINUS
    elif ch == '*': getChar(); sym = MULT
    # elif ch == '/': getChar(); sym = DIV
    elif ch == '/':
        getChar()
        if ch == '/': 
            while ch != '\n':
                getChar()
            getSym()
        elif ch == '\\': getChar(); sym == AND
        else: sym = DIV
    elif ch == '~':
        getChar()
        if ch == '?': getChar(); sym = ELSE
        else: sym = NOT
    elif ch == '|': 
        getChar(); 
        if ch == '>': getChar(); sym = GE
        else: mark('invalid symbol'); sym = None
    # elif ch == '&': getChar(); sym = AND
    elif ch == '<':
        getChar()
        if ch == '>': getChar(); sym = MOD
        elif ch == '|': getChar(); sym = LE
        else: sym = LT
    elif ch == '>': getChar(); sym = GT
    elif ch == '=': getChar(); sym = EQ

    elif ch == '_': getChar(); sym = BOOL
    elif ch == '.': getChar(); sym = INPUT

    # elif ch == '#': 
    #     getChar(); 
    #     if ch == '#': getChar(); sym == IDENTITY_INT
    #     else: sym = INT
    # elif ch == '%': 
    #     getChar(); 
    #     if ch == '%': getChar(); sym == IDENTITY_FLOAT
    #     else: sym = FLOAT
    # elif ch == '@': 
    #     getChar(); 
    #     if ch == '@': getChar(); sym == IDENTITY_STRING
    #     else: sym = STRING
    # elif ch == '^': 
    #     getChar(); 
    #     if ch == '^': getChar(); sym == IDENTITY_BOOLEAN
    #     else: sym = BOOLEAN
    elif ch == '#': getChar(); sym = INT
    elif ch == '%': getChar(); sym = FLOAT
    elif ch == '@': getChar(); sym = STRING
    elif ch == '^': getChar(); sym = BOOLEAN

    # elif ch == '!': getChar(); sym = PRINT
    elif ch == '!':
        getChar()
        if ch == '[': getChar(); sym = FUNC_DEF
        else: sym = PRINT
    # elif ch == '?': getChar(); sym = IF
    elif ch == '?':
        getChar()
        if ch == '[': getChar(); sym = FUNC_CALL
        else: sym = IF
    elif ch == ']': getChar(); sym = FUNC_END
    elif ch == '$': getChar(); sym = LOOP
    elif ch == '\\': 
        getChar(); 
        if ch == '/': getChar(); sym = OR
        else: sym = EXIT

    elif ch == ';': getChar(); sym = LINEEND
    elif ch == ':': getChar(); sym = COLON
    elif ch == ',': getChar(); sym = COMMA
    elif ch == '(': getChar(); sym = LPAREN
    elif ch == ')': getChar(); sym = RPAREN
    elif ch == '{': getChar(); sym = LCURLY
    elif ch == '}': getChar(); sym = RCURLY
    elif ch == chr(0): sym = EOF
    else: mark('illegal character: '+ch); getChar(); sym = None

# a=1;
# b=5;
# ? a>b {
#   !a;
#   u=a;
#   l=b;
# }
# ~?
#   ? b>a {
#     !b;
#     u=b;
#     l=a;
#   }
#   ~?
#     !'=';
# ? l&u
#   $ l<u::l=l+1:;
# !l;

# t10;
# $ _ : : : {
#   nt/3;
#   ? n>0 t-n
#   ~? t-1;
#   !n;
#   i#.;
#   $ i < 1 & i > 2 : : : i#. ;
#   ? t=0 {!'WIN';\;};
# };


# a,b+1,5;?a>b{!a;u=a;l=b;}~??b>a{!b;{u=b;l=a;}}~?!'=';?l&u$l<u::l=l+1:;!l;
# n,e42+4,#(100/2);?n<1\~??n>99\;!'begin';$~(g=n):ge:?g>n{g-#(e/2);e#(e/2);}~?{g+#(e/2);e#(e/2);}:{!g;?e=0e1;};!@g;!'end';
# t10;$_:::{n#(t/3);?n>0t-#n~?t-1;!n;!t;in;$i>3|i<0:::{?i>3i-1~??i<0i+1~?!'N';!'i'+@i+''+@((i<3&i>0));};?t<0{!'WIN';\;};};
# a,b5,5;$i<a:i0:i+1:$j<b:j0:j+1:!i*' '+@j;
# n20;i0;$(i<n|i=n):i1:i+1:{?i<>15=0!'FizzBuzz'~?{?i<>3=0!'Fizz';?i<>5=0!'Buzz';};};


# t0;!t+10;$_:::{n#(t/3);?n>0t-#n~?t-1;!n;!t;in;$i>3|i<0:::{?i>3i-1~??i<0i+1~?!'N';!'i'+@i+''+@((i<3&i>0));};?t<0{!'WIN';\;};};

# n42+4e#(100/2);?n<1\~??n>99\;!'begin';$~(g=n):ge::{!g;?e=0e1;?g>n{g-#(e/2);e#(e/2);}~?{g+#(e/2);e#(e/2);}};!@g;!'end';

# n20;i0;$(i<n|i=n):i1:i+1:{?i<>15=0!'FizzBuzz'~?{?i<>3=0!'Fizz';?i<>5=0!'Buzz';};};
# a5b5;$i<a:i0:i+1:$j<b:j0:j+1:!i*' '+@j;

# a+1b5?a>b{!a;u=a;l=b;}~??b>a{!b;{ub;la;}}~?!'=';?l&u$l<u::l=l+1:;!l;

#n42+4e#(100/2);?n<1\~??n>99\;!'begin';$~(g=n):ge:?g>n{g-#(e/2);e#(e/2);}~?{g+#(e/2);e#(e/2);}:{!g;?e=0e1;};!@g;!'end';
#n,e42+4,#(100/2);?n<1\~??n>99\;!'begin';$~(g=n):ge:?g>n{g-#(e/2);e#(e/2);}~?{g+#(e/2);e#(e/2);}:{!g;?e=0e1;};!@g;!'end';
#a='';?_f![#:#a%d%e:t=8;!a+d+e\a]~?f![@::\'yo']
