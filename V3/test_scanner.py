import bc3_scanner as SC
from bc3_scanner import *

def test_parseSyntax():
    single_syms = '>< @ | || & && = <> < > + - * / \\ % ^ ! :: -> => <- <= ~ . ( ) [ ] { } , : \n ;'
    single_ans = [ENOT,PARAM,OR,UNION,AND,INTER,EQ,NE,LT,GT,PLUS,MINUS,MULT,DIV,INTDIV,MOD,EXP,NOT,CAST,GOARROW1,GOARROW2,
        RETARROW1,RETARROW2,ARROWSHAFT,NOJUMP,LPAREN,RPAREN,LBRAK,RBRAK,LCURLY,RCURLY,COMMA,COLON,LINEEND,LINEEND]
    SC.init('',single_syms,False)
    for sym in single_ans:
        assert SC.sym == sym
        SC.getSym()

def test_parseKeyword():
    keyword_syms = 'var const in set del goto if try cmp out incl quit retn flag log \n'
    keyword_ans = [VAR,CONST,READ,SET,DEL,GOTO,IF,TRY,EXEC,PRINT,INCLUDE,QUIT,RETURN,RAISE,LOG]
    SC.init('',keyword_syms,False)
    for sym in keyword_ans:
        assert SC.sym == sym
        SC.getSym()

def test_parseType():
    type_syms = 'int str float bool array list null \n'
    type_ans = [INT,STR,FLOAT,BOOL,ARRAY,LIST,NONE]
    SC.init('',type_syms,False)
    for sym in type_ans:
        assert SC.sym == sym
        SC.getSym()

def test_parseLiteral():
    type_syms = '1 111 1.1 1. "string" \'string\' var1 var_1 _var _'
    type_ans = [NUMBER,NUMBER,DECIMAL,DECIMAL,STRING,STRING,IDENT,IDENT,IDENT]
    SC.init('',type_syms,False)
    for sym in type_ans:
        assert SC.sym == sym
        SC.getSym()

def test_parseComment():
    comment_syms = '//var 3 in\n 3.2 /* 3.2 var \n jeb + + */ jess'
    comment_ans = [LINEEND,DECIMAL,IDENT]
    SC.init('',comment_syms,False)
    for sym in comment_ans:
        assert SC.sym == sym
        SC.getSym()

def test_parseError():
    error_syms = '`'
    SC.init('',error_syms,False)
    assert SC.error == True
