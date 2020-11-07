#!/usr/bin/env python
# coding: utf-8

import bc_sc as SC
from bc_sc import ADD, SUB, MULT, DIV, MOD, EXP, AND, OR, NOT, LNOT, FULL_STRING, TRUE, FALSE, EQ, NE, LT, GT, LE_RETARROW2, GE, LPAREN, RPAREN, LBRAK, RBRAK, LCURLY, RCURLY, PERIOD, COMMA, COLON, DOUBLE_COLON, SEMICOLON, IDENT, NUMBER, INT, FLOAT, BOOL, STRING, ARRAY, LIST, GOARROW1, GOARROW1_SHAFT, RETARROW1, GOARROW2, GOARROW2_SHAFT, VAR, ASSIGN, GOTO, PRINT, READ, IF, COMPARE, DELETE, TRY, INCLUDE, PARAM, LEN, TYPE, LABEL, NULL, EOF, getSym, mark
import bc_st as ST
from bc_st import  newDecl, newJump, findDecl, findJump, delDecl, assignDecl, Collection

# ngl bytecode interpreter
# Does an initial first pass to find all go arrows and return arrows

FIRSTATOM = {NUMBER,IDENT,FULL_STRING,NOT,TRUE,FALSE,LPAREN,LCURLY}
FOLLOWATOM = {NUMBER,IDENT,FULL_STRING,TRUE,FALSE,RPAREN,RCURLY,INT,FLOAT,STRING,BOOL,ARRAY,LIST,RBRAK}
FIRSTSTMT = {VAR,ASSIGN,GOTO,PRINT,READ,IF,DELETE,TRY,COMPARE}
FIRSTFUNC = {LABEL,TYPE}

FIRSTLINE = FIRSTSTMT

FIRSTPROGRAM = {IDENT, GOARROW1, GOARROW2, RETARROW1, LE_RETARROW2} | FIRSTLINE
FOLLOWLINE = {SEMICOLON}

FIRSTEXPR = {ADD,SUB} | FIRSTATOM | FIRSTFUNC
FOLLOWEXPR = FOLLOWATOM

FOLLOWSTMT = FOLLOWEXPR | {GOARROW1, GOARROW2, GOARROW1_SHAFT, GOARROW2_SHAFT, RETARROW1, LE_RETARROW2, SUB, EQ}; #TODO: SUB and EQ may cause problems

TYPES = {INT,FLOAT,STRING,BOOL}

# TODO: make labels save pos so labels can exist in a line
# TODO: add proper null type
# TODO: Move FUNC to ATOM?

# Complex operator
    # len:: - find length
    # lab:: - find line location of label
    # typ:: - find type

# PROGRAM ::= {[(<- | <=){0,2}][IDENT ':'] LINE}
def program():
    while True:
        # print(SC.sym,SC.val)
        if SC.sym in FIRSTPROGRAM :
            if SC.sym in (RETARROW1, LE_RETARROW2, GOARROW1, GOARROW2):
                getSym()
            if SC.sym in (RETARROW1, LE_RETARROW2, GOARROW1, GOARROW2):
                getSym()
            if SC.sym == IDENT:
                # newJump(SC.val,SC.line)
                getSym()
                if SC.sym != COLON: mark('missing colon')
                getSym()

            if SC.sym == EOF: break
            if SC.sym in FIRSTLINE:
                line()

        elif SC.sym == EOF: break
        else: mark('invalid command'); print(SC.sym,SC.val); getSym()

# LINE ::= STMT ';' | '\n'
def line():

    stmt()

    if SC.sym != SEMICOLON: mark('missing semicolon'); print(SC.sym)
    else: getSym()

# stmt ::= var IDENT TYPE EXPR
#        | set IDENT EXPR
#        | goto LABEL
#        | if EXPR LABEL
#        | cmp EXPR
#        | print EXPR
#        | read IDENT TYPE
#        | del IDENT
#        | incl FULL_STRING
def stmt():
    if SC.sym not in FIRSTSTMT | {SEMICOLON}: mark('unknown command');

    if SC.sym == VAR or SC.sym == ASSIGN:
        op = SC.sym
        getSym()
        if SC.sym != IDENT:
            mark('invalid identifier')
        else:
            name = SC.val
        getSym()

        if op == VAR:
            if SC.sym != DOUBLE_COLON: mark('missing type specifier')
            typ = cast()
            if typ in {ARRAY, LIST}: mark('invalid primative'); typ = STRING

            collection = False
            if SC.sym == DOUBLE_COLON:
                set_typ = cast()
                if set_typ not in {ARRAY, LIST}: mark('invalid collection')
                else:
                    collection = True
                    if set_typ == ARRAY:    edit = False
                    else:               edit = True

            value = None
            if SC.sym not in FOLLOWLINE:
                value,n_typ = expr()

                if collection and typ != n_typ: mark('mismatch between declared type and set type')

                if typ != n_typ:
                    mark('mismatched variable type')
                    typ=n_typ

            newDecl(name,typ,value)

        elif op == ASSIGN:
            if SC.sym == LBRAK: index = spec()
            else: index = None

            value, typ = expr()

            if type(value) == Collection and index != None: mark('nested collections are not allowed')
            else:
                old_value,old_typ = findDecl(name)

                if (typ != old_typ) and (type(old_value) == Collection or type(value) == Collection):
                    mark('assignment of non-collection to collection')
                elif index: assignDecl(name,typ,value,index)
                else: assignDecl(name,typ,value)

    elif SC.sym == GOTO:
        getSym()
        line = label()

        SC.set_goto(line)

    elif SC.sym == IF or SC.sym == COMPARE:
        if SC.sym == IF:    isIf = True
        else:               isIf = False
        getSym()
        value,typ = expr()

        if isIf: # IF will jump, cmp can just cause errors
            line = label()

            if typ == BOOL:
                if value == True:
                    SC.set_goto(line)
            else: mark('non-boolean jump condition')

    elif SC.sym == READ:
        getSym()
        if SC.sym != IDENT: mark('invalid identifier')
        else: name = SC.val
        getSym()

        if SC.sym != DOUBLE_COLON: mark('missing type specifier')
        typ = cast()

        value = input()

        try:
            if typ == INT:      value = int(value)
            elif typ == FLOAT:  value = float(value)
            elif typ == BOOL:   value = bool(value)
            elif typ == STRING: value = str(value)
            else: mark('invalid primative')
        except ValueError:
            mark('invalid conversion')
            if type(value) == float: typ = FLOAT
            if type(value) == int: typ = INT
            if type(value) == str: typ = STRING
            if type(value) == bool: typ = BOOL

        newDecl(name,typ,value)

    elif SC.sym == DELETE:
        getSym()
        if SC.sym != IDENT: mark('invalid identifier')
        else: name = SC.val
        getSym()

        delDecl(name)

    elif SC.sym == PRINT:
        getSym()
        value,typ = expr()
        print(value)

    elif SC.sym == TRY:
        getSym()

        old_error, SC.supress = SC.error, True

        stmt()
        line = label()

        if SC.error:
            SC.set_goto(line)

        SC.error, SC.supress = old_error, False

    elif SC.sym == INCLUDE:
        getSym()

        if SC.sym == FULL_STRING: getSym()
        else:
            mark('include requires file name')
            if SC.sym != COLON: getSym()

# LABEL ::= IDENT | '->' | '=>' | '<-' | '<='
def label():
    if SC.sym == IDENT:
        line = findJump(SC.val)
        getSym()
    elif SC.sym == GOARROW1 or SC.sym == GOARROW1_SHAFT: # ->
        back = 0
        if SC.sym == GOARROW1_SHAFT:
            while SC.sym == GOARROW1_SHAFT: getSym(); back+=1
            if SC.sym == GOARROW1: getSym()
            else: mark('arrow head expected')
        else: getSym()
        line = findJump('<-',SC.line,back)
    elif SC.sym == GOARROW2 or SC.sym == GOARROW2_SHAFT: # =>
        back = 0
        if SC.sym == GOARROW2_SHAFT:
            while SC.sym == GOARROW2_SHAFT: getSym(); back+=1
            if SC.sym == GOARROW2: getSym()
            else: mark('arrow head expected')
        else: getSym()
        line = findJump('<=',SC.line,back)
    elif SC.sym == RETARROW1: # <-
        getSym()
        back = 0
        # Last shaft will count as SUB
        while SC.sym in {SUB, GOARROW1_SHAFT}: getSym(); back+=1
        line = findJump('->',SC.line,back)
    elif SC.sym == LE_RETARROW2: # <=
        getSym()
        back = 0
        while SC.sym in {EQ, GOARROW2_SHAFT}: getSym(); back+=1
        line = findJump('=>',SC.line,back)
    else:
        mark('unknown label')
        line = SC.line
        getSym()

    return line

# EXPR ::= [!] COMPARE {('&' | '|') COMPARE}
def expr():
    if SC.sym not in FIRSTEXPR: mark('invalid expression'); print(SC.sym); return
    if SC.sym == LNOT: invert = True; getSym()
    else: invert = False

    value,typ = compare()
    while SC.sym == AND or SC.sym == OR:
        op = SC.sym
        getSym()
        mod,typ2 = compare()
        if typ == BOOL and typ2 == BOOL:
            if op == AND: value = value and mod
            elif op == OR: value = value or mod
        else:
            mark('invalid use of boolean operation')

    if invert:
        if typ != BOOL: mark('non-bool inversion')
        else: value = not value

    return (value,typ)

# compare ::= MATHEMATICAL [('=' | '!=' | '<' | '>' | '<=' | '>=') MATHEMATICAL]
def compare():
    value,typ = mathematical()
    if SC.sym in {EQ,NE,LT,GT,LE_RETARROW2,GE}:
        op = SC.sym
        getSym()
        mod,typ2 = mathematical()
        # TODO: Wider type compatability
        if typ in {INT, FLOAT} and typ2 in {INT,FLOAT}:
            if op == EQ: value = value == mod
            elif op == NE: value = value != mod
            elif op == LT: value = value < mod
            elif op == GT: value = value > mod
            elif op == LE_RETARROW2: value = value <= mod
            elif op == GE: value = value >= mod
            typ = BOOL
        else:
            mark('invalid use of boolean operation')

    return (value,typ)

# mathematical ::= ['+' | '-'] TERM {('+' | '-') TERM}
def mathematical():
    if SC.sym == SUB: getSym(); mult=-1
    else:
        if SC.sym == ADD: getSym()
        mult = 1
    value,typ = term()
    if typ in {INT,FLOAT}:
        value = mult * value
    elif mult == -1 and typ not in {INT,FLOAT}:
        mark('invalid use of negation')

    while SC.sym == ADD or SC.sym == SUB:
        op = SC.sym
        getSym()
        mod,typ2 = term()
        # TODO: Wider type compatability
        if typ in {INT, FLOAT} and typ2 in {INT,FLOAT}:
            if op == ADD: value += mod
            elif op == SUB: value -= mod

            if type(value)==int: typ = INT
            elif type(value)==float: typ = FLOAT
        elif typ == typ2 == STRING:
            if op == ADD: value += mod
            else: mark('invalid use of operation')
        else:
            mark('invalid use of operation')

    return (value,typ)

# TERM ::= FACTOR {('*' | '/' | '%') FACTOR}
def term():
    value,typ = factor()
    while SC.sym == MULT or SC.sym == DIV or SC.sym == MOD:
        op = SC.sym
        getSym()
        mod,typ2 = term()
        # TODO: Wider type compatability
        if typ in {INT, FLOAT} and typ2 in {INT,FLOAT}:
            if op == MULT: value *= mod
            elif op == DIV: value /= mod
            elif op == MOD: value %= mod

            if type(value)==int: typ = INT
            elif type(value)==float: typ = FLOAT
        else:
            mark('invalid use of operation')

    return (value,typ)

# FACTOR ::= FUNC [^ FUNC]
def factor():
    value, typ = func()
    if SC.sym == EXP:
        getSym()
        exponent, typ2 = func()
        if typ2 not in {INT,FLOAT}:
            mark('non-numerical exponent')
        else:
            nvalue = value ** exponent
            # TODO: Wider type compatability
            if type(result)==int: typ = INT; value = nvalue
            elif type(result)==float: typ = FLOAT; value = nvalue
            else: mark('unknown exponent result');

    return (value,typ)

# FUNC ::= [CMD '#'] RESOL {'#' RESOL}
def func():
    if SC.sym in FIRSTFUNC:
        func, arg = SC.sym, []
        getSym()
        if SC.sym == PARAM: getSym()
        else:
            mark('missing parameter marker')
            if SC.sym not in FIRSTATOM: getSym()
    else:
        func = None

    value,typ = resol()
    if func:
        arg.append((value,typ))
        while SC.sym == PARAM:
            getSym()
            n_value,n_typ = resol()
            arg.append((n_value,n_typ))

        if func == LABEL:
            length = 1
            if len(arg) < length: mark('requires '+length+' argument')
            elif arg[0][1] != STRING: mark('incorrect arg type')
            elif arg[0][0] in {'->', '<-', '=>', '<='}: mark('cannot find arrow locations')
            else: line = findJump(arg[0][0]); value, typ = line, INT
        elif func == TYPE:
            length = 2
            if len(arg) < length: mark('requires '+length+' argument')
            elif arg[0][1] == arg[1][1]:  value,typ = True,BOOL
            else:                       value,typ = False,BOOL


    return (value,typ)

# RESOL ::= ATOM {CAST}
def resol():
    value,typ = atom()

    while SC.sym == DOUBLE_COLON:
        n_typ = cast()

        try:
            if n_typ == INT:
                value,typ = int(value),n_typ
            elif n_typ == FLOAT:
                value,typ = float(value),n_typ
            elif n_typ == BOOL:
                value,typ = bool(value),n_typ
            elif n_typ == STRING:
                value,typ = str(value),n_typ
            elif type(value) == Collection:
                if n_typ == ARRAY:
                    value = Collection(False,value.collect)
                elif n_typ == LIST:
                    value = Collection(True,value.collect)
                else:
                    mark('invalid cast primative for collection')
            else:
                if n_typ == ARRAY:
                    value = Collection(False,[value])
                elif n_typ == LIST:
                    value = Collection(True,[value])
                else:
                    mark('invalid cast primative')
        except ValueError: mark('invalid cast')

    return value,typ

# ATOM ::= NUMBER
#        | IDENT SPEC
#        | STRING
#        | ['~'] EXPR
#        | TRUE | FALSE
#        | '(' EXPR ')'
#        | '{' [EXPR {',' EXPR}] '}'
def atom():
    if SC.sym == NUMBER or SC.sym == FULL_STRING:
        if SC.sym == NUMBER and type(SC.sym) == int: typ = INT
        elif SC.sym == NUMBER and type(SC.sym) != int: typ = FLOAT
        else: typ = STRING
        value = SC.val
        getSym()
    elif SC.sym == IDENT:
        value, typ = findDecl(SC.val)
        if value == None and typ !=NULL: mark('use of unitialized variable'); value = ''; typ = STRING # TODO: add proper 'null' value
        getSym()

        if SC.sym == LBRAK:
            index = spec()
            try: value = value[index]
            except IndexError: mark('index out of range')

    elif SC.sym == NOT:
        getSym()
        value,typ = expr()
        if (typ!=BOOL):
            mark('non-bool inversion')
            value = bool(value)
        value,typ = True != value, BOOL

    elif SC.sym == TRUE:
        value,typ = True, BOOL
        getSym()
    elif SC.sym == FALSE:
        value,typ = False, BOOL
        getSym()

    elif SC.sym == LPAREN:
        getSym()
        value,typ = expr()
        if SC.sym == RPAREN: getSym()
        else: mark('missing closing bracket')

    elif SC.sym == LCURLY:
        set_elem,typ = mset()
        value = Collection(True,set_elem) # TODO: Add cast for array and lists

    else:
        mark('unkown atom'); print(SC.sym);
        value, typ = 0,INT

    return (value, typ) # result

# CAST ::= '::' PRIMATIVE
def cast():
    if SC.sym == DOUBLE_COLON: getSym()
    else: mark('missing resolution')

    if SC.sym == INT:
        getSym(); typ = INT
    elif SC.sym == FLOAT:
        getSym(); typ = FLOAT
    elif SC.sym == BOOL:
        getSym(); typ = BOOL
    elif SC.sym == STRING:
        getSym(); typ = STRING
    elif SC.sym == ARRAY: # NOTE: Handle better? They arent really types
        getSym(); typ = ARRAY
    elif SC.sym == LIST: # NOTE: Handle better? They arent really types
        getSym(); typ = LIST
    else:
        mark('invalid primative'); typ = STRING

    return typ

# SPEC ::= '[' EXPR ']'
def spec():
    if SC.sym == LBRAK: getSym()
    else: mark('missing initial brace')

    index,index_typ = expr()
    if index_typ != INT: mark('non-iteger index')

    if SC.sym == RBRAK: getSym()
    else: mark('missing closing brace')

    return index

# MSET ::= '{' ([EXPR {',' EXPR}] | EXPR ':' EXPR CAST ) '}'
def mset():
    if SC.sym == LCURLY: getSym()
    else: mark('missing initial curly brace')

    set_elem, set_typ = [], None

    if SC.sym == DOUBLE_COLON:
        set_typ = cast()
        if set_typ not in {INT, FLOAT, STRING, BOOL}:
            mark('invalid primative')
            set_typ = STRING
    else: mark('Missing collection type')

    if SC.sym == COLON or SC.sym in FIRSTEXPR:
        if SC.sym in FIRSTEXPR: mark('missing collection colon')
        else: getSym()

        first_value,first_typ = expr()

        if SC.sym == COLON:
            getSym();
            end,typ2 = expr()
            if first_typ == typ2 == INT:
                set_elem = list(range(first_value,end+1))
                for i in range(len(set_elem)):
                    if set_typ == INT: set_elem[i] = 0
                    elif set_typ == FLOAT: set_elem[i] = 0.0
                    elif set_typ == STRING: set_elem[i] = ''
                    else: set_elem[i] = False # BOOL

            else: mark('non-integer bounds')
        else:
            set_elem.append(first_value)
            while SC.sym == COMMA:
                getSym()
                value,typ = expr()

                if set_typ != typ: mark('mismatch set type')
                else: set_elem.append(value)

    if SC.sym == RCURLY: getSym()
    else: mark('missing closing curly brace')

    return (set_elem, set_typ)

def execute(src):
    SC.init(src)
    ST.init(src)

    program()

def execute_debug(src):
    from time import time
    import re

    # newsrc = []
    # re_incl = ('incl\s+\'(.*)\'\s*;')
    # isIncl = re.compile(re_incl)
    # for i,line in enumerate(src.splitlines()):
    #     result = isIncl.match(line)
    #     if result:
    #         name = result.group(1) + '.bc'
    #         with open(name,'r') as text:
    #             for subline in text.readlines():
    #                 subline = subline.replace('\n','')
    #                 newsrc.append(subline)
    #     else:
    #         newsrc.append(line)
    #
    # for line in newsrc:
    #     print(line)
    # print()
    #
    # src = '\n'.join(newsrc)

    SC.init(src)
    ST.init(src)

    start = time()
    program()
    end = time()

    print("=====")
    print(end-start,end='s\n')
    if SC.error:
        print('error executing file')
    ST.printSymTab()
    ST.printJmpTab()

if __name__ == '__main__':

    src = '''

var arg1::str 'start';

goto _len;
print result;

start:
'''

    execute_debug(src)

# src='''
# //len.bc
#
# var _arg1::str 'Jason is Cool';
# var result::int 0;
# var i::int 0;
#
# -> try cmp _arg1[i]::bool =>;
# <- set i i+1;
# goto <-;
# <= set result i;
#
# print result;
#
# end: print 'done';
# '''

#     src = '''
# print 'Enter a number between [1,99] for the computer to guess';
# read num::int;
# var guess::int 50;
# var isHigher::bool false;
#
# if num < 1  end;
# if num > 99 end;
#
# print 'Begin Game!';
# print guess;
# goto guesslogic;
#
# feedback:
# if num > guess ->;
# set isHigher false;
# goto genguess;
# <- set isHigher true;
#
# genguess:
# if isHigher ->;
# set guess guess - (guess/2)::int;
# goto =>;
# <- set guess guess + (guess/2)::int;
# <= print guess;
#
# guesslogic:
# if guess > num goDown;
# if guess < num goUp;
# goto end;
# goDown: print 'Lesser';
# goto feedback;
# goUp: print 'Greater';
# goto feedback;
#
# end:
# print 'Finish!';
# '''
