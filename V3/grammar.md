# NGL Bytecode Grammar 3.0

<!-- Note: All setup, like jumpable start + end and boolean constants should be done in PROG preprocess -->

### Productions
Below is the list of productions in the 3rd version of NGL. Above each production will be a small description of what that production will match and three bullet points. The first bullet is the set of terminals which can begin the production, the second is the set of terminals which can end the production and the last is the set of terminals which can follow the production. When referencing other productions in follows, they refer to the first set. The start symbol is `PROG`.

```
The program is separated into a number of lines.
FIRST  = (LINE)
LAST   = (LINE)
FOLLOW = {}
PROG    ::= {LINE}

Each line can have a number of arrows or a label in addition to a statement.
FIRST  = {<-, <=, ->, =>, IDENT} | (STMT)
LAST   = {:} | (ARROW) | (LINEEND)
FOLLOW = (LINE)
LINE    ::= {<- | <= | -> | =>} [IDENT ':'] [STMT] LINEEND

A label is an arrow or an identifier. Note that the identifier namespace and variable namespace is separate. There are two types of arrows which do not interact, allowing for nesting. A tilde can be used to skip multiple arrows and a period will not skip.
FIRST  = (ARROW) | (IDENT)
LAST   = (ARROW) | (IDENT)
FOLLOW = {:} | (LINEEND)
LABEL   ::= IDENT
          | {'~'} ('->' | '=>')
          | ('<-' | '<=') {'~'}
          | '.'

There are a multitude of supported statements. New to 3.0, 'read' becomes 'in', 'print' becomes 'out', the addition of 'retn', 'const', 'flag'.
FIRST  = {var, const, in, set, del, goto, if, try, cmp, out, incl, quit, retn, log}
LAST   = {retn, quit} | (EXPR) | (IDENT) | (LABEL)
FOLLOW = (LINEEND)
STMT    ::= 'var'   IDENT ['::'] TYPE [EXPR] // Create new variable with optional initial value
          | 'const' IDENT ['::'] TYPE EXPR   // Create new constant
          | 'in'    EXPR_L9             // Assign input to a var
          | 'set'   IDENT EXPR          // Set a new variable value
          | 'del'   IDENT               // Delete a variable's record
          | 'goto'  LABEL               // Jump to the corresponding label
          | 'if'    EXPR  LABEL         // Evaluate boolean expression and jump to label if true
          | 'cmp'   EXPR                // Evaluates an expression
          | 'try'   STMT  LABEL         // Evaluate a statement and if there is an error, jump to label
          | 'out'   EXPR                // Outputs an expression result to stdout
          | 'incl'  IDENT {IDENT}       // Imports file(s) as an executable function
          | 'quit'                      // Stops execution of entire trace
          | 'retn'                      // Stops execution of the subfile (TBD)
          | 'log'   EXPR                // Outputs an expression result to errout (TBD)

Lowest precedence is an operator which negates the entire expression
FIRST  = { ><, +, -, !, NUMBER, IDENTIFIER, STRING, (, {, ] }
LAST   = { NUMBER, IDENTIFIER, STRING, ), }, ] }
FOLLOW = (LINEEND)
EXPR    ::= ['><'] EXPR_L0

Function calls are the next lowest. They are so low because the EXPR children should be able to compute calculations of their own.
FIRST  = { +, -, !, NUMBER, IDENTIFIER, STRING, (, {, ] }
LAST   = { NUMBER, IDENTIFIER, STRING, ), }, ] }
FOLLOW = (LINEEND)
EXPR_L0 ::= EXPR_S1 ['@' EXPR {',' EXPR}]

Logical OR for booleans.
FIRST  = { +, -, !, NUMBER, IDENTIFIER, STRING, (, {, ] }
LAST   = { NUMBER, IDENTIFIER, STRING, ), }, ] }
FOLLOW = { @, , } | (LINEEND)
EXPR_S1 ::= EXPR_L1 {('|') EXPR_L1}

Logical AND for booleans.
FIRST  = { +, -, !, NUMBER, IDENTIFIER, STRING, (, {, ] }
LAST   = { NUMBER, IDENTIFIER, STRING, ), }, ] }
FOLLOW = { |, @, , } | (LINEEND)
EXPR_L1 ::= EXPR_S2 {'&' EXPR_S2}

Union for collections.
FIRST  = { +, -, !, NUMBER, IDENTIFIER, STRING, (, {, ] }
LAST   = { NUMBER, IDENTIFIER, STRING, ), }, ] }
FOLLOW = { |, &, @, , } | (LINEEND)
EXPR_S2 ::= EXPR_L2 {('||') EXPR_L2}

Intersection for collections.
FIRST  = { +, -, !, NUMBER, IDENTIFIER, STRING, (, {, ] }
LAST   = { NUMBER, IDENTIFIER, STRING, ), }, ] }
FOLLOW = { |, ||, &, @, , } | (LINEEND)
EXPR_L2 ::= EXPR_L3 {'&&' EXPR_L3}

Equality and inequality operators. When multiple are used, the individual operators are taken in disjunction, so "a = b <> c <> a" evaluates to "a = b & b <> c & c <> a".
FIRST  = { +, -, !, NUMBER, IDENTIFIER, STRING, (, {, ] }
LAST   = { NUMBER, IDENTIFIER, STRING, ), }, ] }
FOLLOW = { &, &&, |, ||, @, , } | (LINEEND)
EXPR_L3 ::= EXPR_L4 {('=' | '<>') EXPR_L4}

Comparsions are similar to equality operators in that they are taken as a disjunction.
FIRST  = { +, -, !, NUMBER, IDENTIFIER, STRING, (, {, ] }
LAST   = { NUMBER, IDENTIFIER, STRING, ), }, ] }
FOLLOW = { =, <>, &, &&, |, ||, @, , } | (LINEEND)
EXPR_L4 ::= EXPR_L5 {('>' | '<') EXPR_L5}

Simple addition and subtraction.
FIRST  = { +, -, !, NUMBER, IDENTIFIER, STRING, (, {, ] }
LAST   = { NUMBER, IDENTIFIER, STRING, ), }, ] }
FOLLOW = { >, <, =, <>, &, &&, |, ||, @, , } | (LINEEND)
EXPR_L5 ::= EXPR_L6 {('+' | '-') EXPR_L6}

Simple multiplication, decimal and integer division and remainder
FIRST  = { +, -, !, NUMBER, IDENTIFIER, STRING, (, {, ] }
LAST   = { NUMBER, IDENTIFIER, STRING, ), }, ] }
FOLLOW = { +, -, >, <, =, <>, &, &&, |, ||, @, , } | (LINEEND)
EXPR_L6 ::= EXPR_L7 {('*' | '/' | '\' | '%') EXPR_L7}

Exponentiation.
FIRST  = { +, -, !, NUMBER, IDENTIFIER, STRING, (, {, ] }
LAST   = { NUMBER, IDENTIFIER, STRING, ), }, ] }
FOLLOW = {*, /, \, %, +, -, >, <, =, <>, &, &&, |, ||, @, , } | (LINEEND)
EXPR_L7 ::= EXPR_L8 {'^' EXPR_L8}

Mathematical unary operators, positive, negative and logical NOT.
FIRST  = { +, -, !, NUMBER, IDENTIFIER, STRING, (, {, ] }
LAST   = { NUMBER, IDENTIFIER, STRING, ), }, ] }
FOLLOW = {^, *, /, \, %, +, -, >, <, =, <>, &, &&, |, ||, @, , } | (LINEEND)
EXPR_L8 ::= ['+' | '-' | '!'] EXPR_L9

Type casting to a primitive or collection.
FIRST  = { NUMBER, IDENTIFIER, STRING, (, {, [ }
LAST   = { NUMBER, IDENTIFIER, STRING, ), }, ] }
FOLLOW = {^, *, /, \, %, +, -, >, <, =, <>, &, &&, |, ||, @, , } | (LINEEND)
EXPR_L9 ::= SUBATOM ['::' TYPE]

Indexing. Available for strings, integers and floats
FIRST  = { NUMBER, IDENTIFIER, STRING, (, {, [ }
LAST   = { NUMBER, IDENTIFIER, STRING, ), }, ] }
FOLLOW = {^, *, /, \, %, +, -, >, <, =, <>, &, &&, |, ||, @, ::, ,} | (LINEEND)
SUBATOM ::= ATOM [ '[' EXPR ']' ]

The highest precidence. Elements are numbers, identifiers, raw strings, parentheses and collections.
FIRST  = { NUMBER, IDENTIFIER, STRING, (, {, [ }
LAST   = { NUMBER, IDENTIFIER, STRING, ), }, ] }
FOLLOW = {[, ^, *, /, \, %, +, -, >, <, =, <>, &, &&, |, ||, @, ::, , } | (LINEEND)
ATOM    ::= NUMBER
          | DECIMAL
          | IDENT
          | STRING
          | '(' EXPR ')'
          | '{' PRIME ['::' COLLECT] ':' [ EXPR [({',' EXPR} | ':' EXPR)] ] '}'
          | '[' [ EXPR {',' EXPR} ] ']'


States a basic type or collection type.
FIRST  = {int, float, str, bool, func, label, list}
LAST   = {int, float, str, bool, func, label, list, array}
FOLLOW = (EXPR) | (LINEEND)
TYPE    ::= PRIME ['::' COLLECT]

PRIME   ::= 'int'
          | 'float'
          | 'str'
          | 'bool'
          | 'func'
          | 'label'
          | 'list')

COLLECT ::= 'array'

Definition of a number.
NUMBER  ::= (0-9)+ ['.' (0-9)*]

Definition of an identifier.
IDENT   ::= (a-zA-Z_) {a-zA-Z0-9_}

Definition of a raw string.
STRING  ::= '\'' .* '\''
          | '"' .* '"'

Delineates lines.
LINEEND ::= ';' ['\n']
          | '\n'
```
