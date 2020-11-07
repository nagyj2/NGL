# NGL Bytecode 2.0 Interpreter

import bc2_sc as SC
from bc2_sc import PLUS, MINUS, MULT, DIV, MOD, EXP, AND, OR, NOT, E_NOT, EQ, NE, LT, GT, GOARROW1, GOARROW2, RETARROW1, RETARROW2, ARROW_SHAFT, NOJUMP, COMMA, COLON, CAST, SEMICOLON, PARAM, LPAREN, RPAREN, LBRAK, RBRAK, LCURLY, RCURLY, INT, FLOAT, BOOL, STRING, ARRAY, LIST, NULL, NUMBER, RAW_STRING, BOOLEAN, IDENT, VAR, SET, GOTO, IF, COMPARE, PRINT, READ, DELETE, TRY, RETURN, TYPE, LABEL, LEN, EOF, getSym, mark
import bc2_st as ST
from bc2_st import newDecl, newJump, findDecl, findJump, pollJump, delDecl, assignDecl, Variable, Collection
import bc2_pp as PP
from bc2_sk import FIRSTPRIMATIVE, FOLLOWPRIMATIVE, FIRSTCOLLECTION, FOLLOWCOLLECTION, FIRSTARROW, FOLLOWARROW, FIRSTLABEL, FOLLOWLABEL, FIRSTINDEX, FOLLOWINDEX, USRFUNC, FIRSTFUNC, FOLLOWFUNC, FIRSTFULL_TYPE, FOLLOWFULL_TYPE, FIRSTCAST_TYPE, FOLLOWCAST_TYPE, FIRSTATOM, FOLLOWATOM, FIRSTSUBATOM, FOLLOWSUBATOM, FIRSTEXPR_L7, FOLLOWEXPR_L7, FIRSTEXPR_L6, FOLLOWEXPR_L6, FIRSTEXPR_L5, FOLLOWEXPR_L5, FIRSTEXPR_L4, FOLLOWEXPR_L4, FIRSTEXPR_L3, FOLLOWEXPR_L3, FIRSTEXPR_L2, FOLLOWEXPR_L2, FIRSTEXPR_L1, FOLLOWEXPR_L1, FIRSTEXPR, FOLLOWEXPR, FIRSTSTMT, FOLLOWSTMT, FIRSTLINE, FOLLOWLINE, FIRSTPROGRAM, FOLLOWPROGRAM
import bc2_lib as LIB

# calls = 0
# def call(func):
#     def wrapper():
#         global calls
#         calls += 1
#         w1,w2 = func()
#     return wrapper


#@call
def program():
    while SC.sym in FIRSTPROGRAM:

        while SC.sym in FIRSTARROW:
            # arrow() - dont care about outcome
            getSym()

        if SC.sym == IDENT:
            getSym()
            # if SC.sym == COLON:
            getSym()

        elif SC.sym in FIRSTLINE:
            line()

#@call
# def arrow():
#     if SC.sym == GOARROW1: getSym()
#     elif SC.sym == GOARROW2: getSym()
#     elif SC.sym == RETARROW1: getSym()
#     else: getSym() # SC.sym == RETARROW2

#@call
def line():

    stmt()

    #if SC.sym == SEMICOLON:
    getSym()

#@call
def stmt():
    if SC.sym == VAR:
        getSym()

        #if SC.sym == IDENT:
        name = SC.val
        getSym()

        #if SC.sym in FIRSTCAST_TYPE:
        typ,set_typ = cast_type()

        if SC.sym in FIRSTEXPR:
            value = expr()
            if typ != value.typ:
                mark('variable contents type mismatch')
                # typ = value.typ -> No impact at this point

            if set_typ in {ARRAY, LIST} and type(value) == Variable:
                mark('assignment of variable to collection')
                # set_typ = None -> No impact at this point
            elif set_typ == None and type(value) == Collection:
                mark('assignment of collection to variable')
                # set_typ = ARRAY -> No impact at this point
        else:
            if set_typ == None:
                if typ == INT: value = Variable(INT,0)
                elif typ == FLOAT: value = Variable(FLOAT,0.0)
                elif typ == STRING: value = Variable(STRING,'')
                else: value = Variable(BOOL,False) # BOOL
            else:
                value = Collection(typ,[],set_typ)

        newDecl(name,value)

    elif SC.sym == SET:
        getSym()

        # if SC.sym == IDENT:
        name = SC.val
        getSym()

        # if SC.sym in FIRSTEXPR:
        value = expr()

        old_var = findDecl(name)
        if type(old_var) != type(value):
            mark('assignment of collection and non-collection')
        elif old_var.typ != value.typ:
            mark('assignment type mismatch')
        else:
            assignDecl(name,value)

    elif SC.sym == GOTO:
        getSym()

        # if SC.sym in FIRSTLABEL:
        src_line = label()
        # print(line)
        SC.set_goto(src_line)

    elif SC.sym == IF:
        getSym()

        # if SC.sym in FIRSTEXPR:
        cond = expr()

        # if SC.sym in FIRSTLABEL:
        src_line = label()

        if cond.typ != BOOL: mark('condition is non-boolean')
        if bool(cond) == True:
            SC.set_goto(src_line)

    elif SC.sym == COMPARE:
        getSym()

        # if SC.sym in FIRSTEXPR:
        expr()

    elif SC.sym == PRINT:
        getSym()

        # if SC.sym in FIRSTEXPR:
        value = expr()
        print(value)

    elif SC.sym == READ:
        getSym()

        # if SC.sym == IDENT:
        name = SC.val
        getSym()

        # if SC.sym in FIRSTCAST_TYPE:
        typ,set_typ = cast_type()

        value = input() # Always gives string input in python3

        try:
            if set_typ == None:
                if typ == INT:      value = Variable(INT,int(value))
                elif typ == FLOAT:  value = Variable(FLOAT,float(value))
                elif typ == STRING: value = Variable(STRING,str(value))
                elif typ == BOOL:   value = Variable(BOOL,bool(value))
                else: mark('invalid primative')
            else:
                raise Exception('not implemented')
        except ValueError:
            mark('invalid conversion')
            if type(value) == float: typ = FLOAT
            elif type(value) == int: typ = INT
            elif type(value) == str: typ = STRING
            elif type(value) == bool: typ = BOOL

        newDecl(name,value)

    elif SC.sym == DELETE:
        getSym()

        # if SC.sym == IDENT:
        name = SC.val
        getSym()
        delDecl(name)

    elif SC.sym == TRY:
        getSym()
        old_error, SC.supress = SC.error, True

        # if SC.sym in FIRSTSTMT:
        stmt()

        # if SC.sym in FIRSTLABEL:
        src_line = label()

        if SC.error:
            SC.set_goto(src_line)

        SC.error, SC.supress = old_error, False

    else: # SC.sym == RETURN
        getSym()

        src_line = findJump(RETURN,SC.line)
        SC.set_goto(src_line)

#@call
def label():
    # Return src_line
    back = 0
    if SC.sym == IDENT:
        src_line = findJump(SC.val,SC.line)
        getSym()

    elif SC.sym == RETARROW1:
        getSym()
        while SC.sym == ARROW_SHAFT:
            back += 1
            getSym()
        src_line = findJump(RETARROW1,SC.line,back)

    elif SC.sym == RETARROW2:
        getSym()
        while SC.sym == ARROW_SHAFT:
            back += 1
            getSym()
        src_line = findJump(RETARROW2,SC.line,back)

    elif SC.sym == GOARROW1:
        src_line = findJump(GOARROW1,SC.line,back)
        getSym()

    elif SC.sym == GOARROW2:
        src_line = findJump(GOARROW2,SC.line,back)
        getSym()

    elif SC.sym == ARROW_SHAFT:
        while SC.sym == ARROW_SHAFT:
            back += 1
            getSym()

        if SC.sym == GOARROW1:
            src_line = findJump(GOARROW1,SC.line,back)
        else: # SC.sym == GOARROW2:
            src_line = findJump(GOARROW2,SC.line,back)
        getSym()

    else: # SC.sym == NOJUMP:
        getSym()
        src_line = SC.line

    return src_line

#@call
def cast_type():
    # Return (primitive type, set type)
    # if SC.sym == CAST:
    getSym()

    # if SC.sym in FIRSTFULL_TYPE:
    typ,set_typ = full_type()
    return (typ,set_typ)

#@call
def full_type():
    # Return (primitive type, set type)
    # if SC.sym in FIRSTPRIMATIVE:
    typ = primative()
    set_typ = None

    if SC.sym == CAST:
        getSym()

        #if SC.sym in FIRSTCOLLECTION:
        set_typ = collection()

    return (typ,set_typ)

#@call
def expr():
    invert = False
    if SC.sym == E_NOT:
        invert = True; getSym()

    value = expr_l1()

    if invert:
        if value.typ == BOOL: value = Variable(BOOL,not value.value)
        else: mark('inversion non-boolean expression')

    return value

#@call
def expr_l1():
    value = expr_l2()
    while SC.sym == OR:
        getSym()
        # if SC.sym in FIRSTEXPR_L1:
        mod = expr_l2()
        if value.typ == BOOL: value = value or mod
        else: mark('disjunction of non-boolean')

    return value

#@call
def expr_l2():
    value = expr_l3()
    while SC.sym == AND:
        getSym()
        #if SC.sym in FIRSTEXPR_L2:
        mod = expr_l3()
        if value.typ == BOOL: value = value and mod
        else: mark('disjunction of non-boolean')

    return value

#@call
def expr_l3():
    value = expr_l4()
    while SC.sym in {EQ, NE, LT, GT}:
        op = SC.sym
        getSym()
        # if SC.sym in FIRSTEXPR_L3:
        mod = expr_l4()
        if (value.typ in {INT, FLOAT} and mod.typ in {INT,FLOAT}) or (value.typ == mod.typ == STRING):
            if op == EQ: value = value == mod
            elif op == NE: value = value != mod
            elif op == LT: value = value < mod
            elif op == GT: value = value > mod
        else: mark('incompatible operand types')

    return value

#@call
def expr_l4():
    sub = False
    if SC.sym == PLUS: getSym()
    elif SC.sym == MINUS: sub = True; getSym()

    value = expr_l5()
    if sub:
        if value.typ in {INT, FLOAT}: value = -value
        else: mark('negation of non-numerical')

    while SC.sym in {PLUS, MINUS}:
        op = SC.sym
        getSym()
        # if SC.sym in FIRSTEXPR_L5:
        mod = expr_l5()
        if op == PLUS: value = value + mod
        elif op == MINUS: value = value - mod

    return value

#@call
def expr_l5():
    value = expr_l6()
    while SC.sym in {MULT, DIV, MOD}:
        op = SC.sym
        getSym()
        # if SC.sym in FIRSTEXPR_L5:
        mod = expr_l6()
        if op == MULT: value = value * mod
        elif op == DIV: value = value / mod
        elif op == MOD: value = value % mod

    return value

#@call
def expr_l6():
    value = expr_l7()
    if SC.sym == EXP:
        getSym()
        #if SC.sym in FIRSTEXPR_L6:
        mod = expr_l7()
        value = value ** mod

    return value

#@call
def expr_l7():
    invert = False
    if SC.sym == NOT:
        getSym()
        invert = True

    value = subatom()
    if invert:
        if value.typ == BOOL: value = Variable(BOOL,not value.value)
        else: mark('inversion of non-boolean')

    return value

#@call
def subatom():
    value = atom()

    while SC.sym in FIRSTCAST_TYPE:
        typ,set_typ = cast_type()

        if typ == INT: value = Variable(INT,int(value))
        elif typ == FLOAT: value = Variable(FLOAT,float(value))
        elif typ == STRING: value = Variable(STRING,str(value))
        else: value = Variable(BOOL,bool(value)) # typ == BOOL

        if set_typ != None: raise Exception("not yet implemented")

    return value

#@call
def atom():
    if SC.sym == NUMBER:
        if type(SC.val) == int: value = Variable(INT, SC.val)
        else: value = Variable(FLOAT, SC.val) # FLOAT
        getSym()

    elif SC.sym == IDENT:
        value = findDecl(SC.val)
        getSym()
        if SC.sym in FIRSTINDEX:
            pos = index()
            value = value[pos]

    elif SC.sym == RAW_STRING:
        value = Variable(STRING, SC.val)
        getSym()
        if SC.sym in FIRSTINDEX:
            pos = index()
            value = value[pos]

    elif SC.sym == BOOLEAN:
        if SC.val == 'true': value = Variable(BOOL, True)
        else: value = Variable(BOOL, False) # false
        getSym()

    elif SC.sym == LPAREN:
        getSym()
        value = expr()
        # if SC.sym == RPAREN:
        getSym()

    elif SC.sym == LCURLY:
        getSym()

        # if SC.sym in FIRSTFULL_TYPE:
        typ, set_typ = full_type()
        if set_typ == None: set_typ = LIST

        # if SC.sym == COLON:
        getSym()

        first = expr()

        if SC.sym == COMMA:
            set_elem = [first]
            while SC.sym == COMMA:
                getSym()
                next_elem = expr()
                if typ == next_elem.typ: set_elem.append(next_elem)
                else: mark('element and collection type mismatch')

        else: # SC.sym == COLON:
            getSym()
            end = expr()

            if not (first.typ == end.typ == INT):
                mark('non-integer bounds')
                start, end = Variable(INT,0), Variable(INT,0)

            set_elem = list(range(first.value,end.value+1))
            for i in range(len(set_elem)):
                if typ == INT: set_elem[i] = Variable(typ,0)
                elif typ == FLOAT: set_elem[i] = Variable(typ,0.0)
                elif typ == STRING: set_elem[i] = Variable(typ,'')
                else: set_elem[i] = Variable(typ,False) # BOOL

        value = Collection(typ,set_elem,set_typ)

        #if SC.sym == RCURLY:
        getSym()

    else: # SC.sym in FIRSTFUNC:
        # func() -> don't need
        fun = SC.sym
        getSym()

        param = []
        while SC.sym == PARAM:
            getSym()

            # if SC.sym in FIRSTEXPR:
            value = expr()
            param.append(value)

        src_line = findJump(RETURN,SC.line)
        if fun == LABEL:

            value = LIB.func_label(param)

        elif fun == LEN:
            value = LIB.func_len(param)

        elif fun == TYPE:
            value = LIB.func_type(param)

    return value

#@call
def index():
    # if SC.sym == LBRAK:
    getSym()

    ind = expr()

    # if SC.sym == RBRAK:
    getSym()
    return ind

#@call
def primative():

    if SC.sym == INT: value = INT; getSym()
    elif SC.sym == FLOAT: value = FLOAT; getSym()
    elif SC.sym == BOOL: value = BOOL; getSym()
    else: value = STRING; getSym() # SC.sym == STRING
    return value

#@call
def collection():
    if SC.sym == ARRAY: value = ARRAY; getSym()
    else: value = LIST; getSym() # SC.sym == LIST
    return value

#@call
# def func():
#     if SC.sym == TYPE: getSym()
#     elif SC.sym == LABEL: getSym()
#     elif SC.sym == LEN: getSym()
#     else: getSym() # SC.sym in USRFUNC

# 476 - 331 = 145 lines saved


def execute_debug(src):
    global calls
    from time import time

    # Run proprocessor
    isError = PP.init(src, debug = True)

    if not isError:
        start = time()
        program()
        end = time()

        print("=RELEASE=")
        print(end-start,end='s\n')
        # print('Calls:',calls)
        if SC.error:
            print('error executing file')
        ST.printSymTab()
        ST.printJmpTab()


if __name__ == '__main__':
    src = ''
    with open('usr.ngl','r') as reader:
        for src_line in reader.readlines():
            src += src_line

    execute_debug(src)

# var fixed::bool true;
# if fixed ->;
# print 'Enter a number between [1,99] for the computer to guess';
# read num::int;
# goto ~->;
# <-
# var num::int 42;
# <-
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
