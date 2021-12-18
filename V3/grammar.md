# NGL Bytecode Grammar 3.0

<!-- Note: All setup, like jumpable start + end and boolean constants should be done in PROG preprocess -->

### Thinkpad
This section is dedicated to potential changes to the grammar.

- Use of backquotes to additionally convert expression results to a string. **implemented**
- Modify `@` operation to ATOM level **implemented**
    - Use of pound, `#`, to represent parameters to the function call operator
    - `#` is the second lowest precidence and `@` is the highest **_half implemented_**
    - `@`'s argument is an identifier or another defined function
- Use of `::=` for type equality. **implemented**
- ~~Inline, ternary if statements with `? EXPR_L8 EXPR : EXPR `~~
- Modify statements to take second EXPR instead of LABELs since the namespace is now shared **implemented**
- Constants or some other way to declare identifiers which cannot be deleted
- Use of `$` to denote end/beginning of a collection **implemented**
    - Use of additional `^` for appending **implemented**
- Modify higher end of precedence level to clarify identifiers can have casts and sequencing **implemented**
- `retn` must take a return value **implemented**
- ~~`load` function for _reti_, _retv_, _argv_, etc...?~~
- `log` statement can print to a specific file **implemented**
- ~~Move backquotes, function call to a higher precedence~~
- Change list literal format -> causes problems for malformed index **implemented**
- Rethink incl format
    - Some way to import file x as string y
    - If possible, have way to import multiple in one statement
    - maybe use comma?
- ~~Function command?~~
- Slices and array ranges use colon instead of tilde **implemented**
    - logical not uses tilde too
- Allow mathematical operators to work with int and float
    - Return type is the first one used
- use ? suffix for burrow **implemented**
- use _glob_ command for global declaration? -> goes to lvl 0 from anywhere **implemented**
    - don't need ? to call back
- allow more slicing
    - second back: arr[$-1]
- Separate type constants from type() and make them expression literals in expressions **implemented**
    - allows recursive casts
        - collection type must be after a base type
    - variables can take type values
    - types can be stored in ST
- nested collections **implemented**
    - nested indexing
- global declaration uses glob before var or const **implemented**

### Productions
Below is the list of productions in the 3rd version of NGL. Above each production will be a small description of what that production will match and three bullet points. The first bullet is the set of terminals which can begin the production, the second is the set of terminals which can end the production and the last is the set of terminals which can follow the production. When referencing other productions in follows, they refer to the first set. The start symbol is `PROG`.

```
FIRST  = (LINE)
LAST   = { EOF }
FOLLOW = {}
PROG    ::= {LINE} EOF

FIRST  = { ->, =>, <-, <=, IDENT } | (STMT)
LAST   = (LINEEND)
FOLLOW = (LINE)
LINE    ::= {<- | <= | -> | =>} [IDENT ':'] [STMT] LINEEND

FIRST  = { ~, ->, =>, <-, <= }
LAST   = { ~, ->, =>, <-, <= }
FOLLOW = (LINEEND)
LABEL   ::= IDENT
          | {'~'} ('->' | '=>')
          | ('<-' | '<=') {'~'}

FIRST  = { var, const, glob, in, set, del, goto, if, cmp, try, out, incl, quit, retn, log }
LAST   = { quit } | (EXPR) | (LABEL)
FOLLOW = (LINEEND)
STMT    ::= ['glob'] 'var'   ELEMENT [EXPR]     // Create new variable with optional initial value (optional global)
          | ['glob'] 'const' ELEMENT EXPR       // Create new constant (optional global)
          | 'in'    ELEMENT                     // Assign input to a var
          | 'set'   INDEXED EXPR                // Set a new variable value
          | ['glob'] 'del'   INDEXED {INDEXED}  // Delete a variable's record
          | 'goto'  LABEL                       // Jump to the corresponding label
          | 'if'    EXPR  LABEL                 // Evaluate boolean expression and jump to label if true
          | 'cmp'   EXPR                        // Evaluates an expression
          | 'try'   STMT  LABEL                 // Evaluate a statement and if there is an error, jump to label
          | 'out'   EXPR                        // Outputs an expression result to stdout
          | ['glob'] 'incl'  IDENT {IDENT}      // Imports file(s) as an executable function
          | 'quit'                              // Stops execution of entire trace
          | 'retn'  EXPR                        // Stops execution of the subfile and returns a value
          | 'log'   EXPR EXPR                   // Outputs an expression result (2nd) to a specified file (1st)

Function calls are the next lowest. They are so low because the EXPR children should be able to compute calculations of their own.
FIRST  = { ><, +, -, ~, NUMBER, DECIMAL, STRING, IDENT, @, (, {, ` }
LAST   = { NUMBER, DECIMAL, STRING, IDENT, \\, ), }, ], ` }
FOLLOW = (LINEEND) | (LABEL) | (EXPR)
EXPR      ::= ['><'] CJN_EXPR

Logical OR for booleans and union for collections.
FIRST  = { +, -, ~, NUMBER, DECIMAL, STRING, IDENT, @, (, {, ` }
LAST   = { NUMBER, DECIMAL, STRING, IDENT, \\, ), }, ], ` }
FOLLOW = (LINEEND) | (LABEL) | (EXPR)
CJN_EXPR  ::= DIS_EXPR {('|' | '||') DIS_EXPR}

Logical AND for booleans and intersection for collections.
FIRST  = { +, -, ~, NUMBER, DECIMAL, STRING, IDENT, @, (, {, ` }
LAST   = { NUMBER, DECIMAL, STRING, IDENT, \\, ), }, ], ` }
FOLLOW = { |, || } | (LINEEND) | (LABEL) | (EXPR)
DIS_EXPR  ::= EQ_EXPR {('&' | '&&') EQ_EXPR}

Equality and inequality operators. When multiple are used, the individual operators are taken in disjunction, so "a = b <> c <> a" evaluates to "a = b & b <> c & c <> a".
FIRST  = { +, -, ~, NUMBER, DECIMAL, STRING, IDENT, @, (, {, ` }
LAST   = { NUMBER, DECIMAL, STRING, IDENT, \\, ), }, ], ` }
FOLLOW = { &, &&, |, || } | (LINEEND) | (LABEL) | (EXPR)
EQ_EXPR   ::= CMP_EXPR {('=' | '<>' | '::=') CMP_EXPR}

Comparsions are similar to equality operators in that they are taken as a disjunction.
FIRST  = { +, -, ~, NUMBER, DECIMAL, STRING, IDENT, @, (, {, ` }
LAST   = { NUMBER, DECIMAL, STRING, IDENT, \\, ), }, ], ` }
FOLLOW = { =, <>, ::=, &, &&, |, || } | (LINEEND) | (LABEL) | (EXPR)
CMP_EXPR  ::= ADD_EXPR {('>' | '<') ADD_EXPR}

Simple addition and subtraction
FIRST  = { +, -, ~, NUMBER, DECIMAL, STRING, IDENT, @, (, {, ` }
LAST   = { NUMBER, DECIMAL, STRING, IDENT, \\, ), }, ], ` }
FOLLOW = { >, <, =, <>, ::=, &, &&, |, || } | (LINEEND) | (LABEL) | (EXPR)
ADD_EXPR  ::= MULT_EXPR {('+' | '-') MULT_EXPR}

Simple multiplication, decimal and integer division and remainder
FIRST  = { +, -, ~, NUMBER, DECIMAL, STRING, IDENT, @, (, {, ` }
LAST   = { NUMBER, DECIMAL, STRING, IDENT, \\, ), }, ], ` }
FOLLOW = { +, -, >, <, =, <>, ::=, &, &&, |, || } | (LINEEND) | (LABEL) | (EXPR)
MULT_EXPR ::= EXP_EXPR {('*' | '/' | '\' | '%') EXP_EXPR}

Exponentiation. Always returns a float
FIRST  = { +, -, ~, NUMBER, DECIMAL, STRING, IDENT, @, (, {, ` }
LAST   = { NUMBER, DECIMAL, STRING, IDENT, \\, ), }, ], ` }
FOLLOW = { *, /, \, %, +, -, >, <, =, <>, ::=, &, &&, |, || } | (LINEEND) | (LABEL) | (EXPR)
EXP_EXPR  ::= UN_EXPR {'**' UN_EXPR}

Mathematical unary operators, positive, negative and logical NOT.
FIRST  = { +, -, ~, NUMBER, DECIMAL, STRING, IDENT, @, (, {, ` }
LAST   = { NUMBER, DECIMAL, STRING, IDENT, \\, ), }, ], ` }
FOLLOW = { **, *, /, \, %, +, -, >, <, =, <>, ::=, &, &&, |, || } | (LINEEND) | (LABEL) | (EXPR)
UN_EXPR   ::= ['+' | '-' | '~'] ELEMENT

Type casting to a primitive or collection.
FIRST  = { NUMBER, DECIMAL, STRING, IDENT, @, (, {, ` }
LAST   = { NUMBER, DECIMAL, STRING, IDENT, \\, ), }, ], ` }
FOLLOW = { **, *, /, \, %, +, -, >, <, =, <>, ::=, &, &&, |, || } | (LINEEND) | (LABEL) | (EXPR)
ELEMENT   ::= INDEXED {'::' INDEXED}

Indexing. Available for strings, integers and floats
FIRST  = { NUMBER, DECIMAL, STRING, IDENT, @, (, {, ` }
LAST   = { NUMBER, DECIMAL, STRING, IDENT, \\, ), }, ], ` }
FOLLOW = { **, *, /, \, %, +, -, >, <, =, <>, ::=, &, &&, |, ||, :: } | (LINEEND) | (LABEL) | (EXPR)
INDEXED   ::= ATOM { '[' INDEX ']' }

The highest precidence. Elements are numbers, identifiers, raw strings, parentheses and collections.
FIRST  = { NUMBER, DECIMAL, STRING, IDENT, @, (, {, ` }
LAST   = { NUMBER, DECIMAL, STRING, IDENT, \\, ), }, `, ? }
FOLLOW = { [, **, *, /, \, %, +, -, >, <, =, <>, ::=, &, &&, |, ||, :: } | (LINEEND) | (LABEL) | (EXPR)
ATOM      ::= NUMBER
            | DECIMAL
            | STRING
            | IDENT ['?']
            | '@' INDEXED {'#' EXPR} ['\\']
            | '(' EXPR ')'
            | '`' EXPR '`'
            | '{' [ELEMENT ':'] [ EXPR [({',' EXPR} | ':' EXPR)] ] '}'

Definition of a valid index
FIRST  = { ^, $ } | (EXPR)
LAST   = { $ } | (EXPR)
FOLLOW = { ] }
INDEX     ::= [^] (EXPR | '$')
            | EXPR [':' (EXPR | '$')]

Definition of a integer.
NUMBER  ::= (0-9)+

Definition of a float.
DECIMAL ::= (0-9)+ (['.' (0-9)*] | 'f')

Definition of an identifier.
IDENT   ::= (a-zA-Z_) {a-zA-Z0-9_}

Definition of a raw string.
STRING  ::= '\'' .* '\''
          | '"' .* '"'

Delineates lines.
LINEEND ::= ';' ['\n']
          | '\n'
```


<!-- States a basic type or collection type.
FIRST  = {int, float, str, bool, func, label, list}
LAST   = {int, float, str, bool, func, label, list, array}
FOLLOW = (EXPR) | (LINEEND)
TYPE      ::= PRIME ['::' COLLECT]

PRIME     ::= 'int'
            | 'float'
            | 'str'
            | 'bool'
            | 'func'
            | 'label'
            | 'list')

COLLECT   ::= 'array' -->
