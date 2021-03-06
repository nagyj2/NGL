from bc3_scanner import Scanner
from bc3_scanner import *

def test_parseSyntax():
    single_syms = '>< @ | || & && = <> < > + - * / \\ % ^ ! :: -> => <- <= ~ . ( ) [ ] { } , : \n ;'
    single_ans = [ENOT,PARAM,OR,UNION,AND,INTER,EQ,NE,LT,GT,PLUS,MINUS,MULT,DIV,INTDIV,MOD,EXP,NOT,CAST,GOARROW1,GOARROW2,
        RETARROW1,RETARROW2,ARROWSHAFT,NOJUMP,LPAREN,RPAREN,LBRAK,RBRAK,LCURLY,RCURLY,COMMA,COLON,NEWLINE,LINEEND]
    SC = Scanner('',single_syms,False)
    for sym in single_ans:
        assert SC.sym == sym
        SC.getSym()

def test_parseKeyword():
    keyword_syms = 'var const in set del goto if try cmp out incl quit retn log \n'
    keyword_ans = [VAR,CONST,READ,SET,DEL,GOTO,IF,TRY,EXEC,PRINT,INCLUDE,QUIT,RETURN,LOG]
    SC = Scanner('',keyword_syms,False)
    for sym in keyword_ans:
        assert SC.sym == sym
        SC.getSym()

def test_parseType():
    type_syms = 'int str float bool array list null \n'
    type_ans = [INT,STR,FLOAT,BOOL,ARRAY,LIST,NONE]
    SC = Scanner('',type_syms,False)
    for sym in type_ans:
        assert SC.sym == sym
        SC.getSym()

def test_parseLiteral():
    type_syms = '1 111 1.1 1. "string" \'string\' var1 var_1 _var _'
    type_ans = [NUMBER,NUMBER,DECIMAL,DECIMAL,STRING,STRING,IDENT,IDENT,IDENT]
    SC = Scanner('',type_syms,False)
    for sym in type_ans:
        assert SC.sym == sym
        SC.getSym()

def test_parseComment():
    comment_syms = '//var 3 in\n 3.2 /* 3.2 var \n jeb + + */ jess'
    comment_ans = [NEWLINE,DECIMAL,IDENT]
    SC = Scanner('',comment_syms,False)
    for sym in comment_ans:
        assert SC.sym == sym
        SC.getSym()

def test_parseError():
    error_syms = '` $'
    SC = Scanner('',error_syms,False)
    assert SC.error == True

def test_reset():
    reset_syms = '2 + 4\n5 * 7'
    reset_ans = [NUMBER,PLUS,NUMBER]
    SC = Scanner('',reset_syms,False)
    for sym in reset_ans:
        assert SC.sym == sym
        SC.getSym()
    SC.reset()
    reset_ans = [NUMBER,PLUS,NUMBER,NEWLINE,NUMBER,MULT,NUMBER]
    for sym in reset_ans:
        assert SC.sym == sym
        SC.getSym()
    SC.setGoto(1)
    SC.execGoto()
    for sym in reset_ans:
        assert SC.sym == sym
        SC.getSym()

def test_progress():
    progress_syms = '2 + 4;\n5 * 7;\n'
    progress_ans1 = [NUMBER,PLUS,NUMBER,LINEEND,NEWLINE]
    progress_ans2 = [NUMBER,MULT,NUMBER,LINEEND,NEWLINE]
    SC = Scanner('',progress_syms,False)
    for sym in progress_ans1:
        assert SC.sym == sym
        SC.getSym()
    # SC.nextLine()
    for sym in progress_ans2:
        assert SC.sym == sym
        SC.getSym()
