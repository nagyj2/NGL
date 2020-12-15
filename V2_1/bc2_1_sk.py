# NGL Bytecode 2.1 Grammar Skeleton (Preprocessor)

import bc2_1_sc as SC
from bc2_1_sc import PLUS, MINUS, MULT, DIV, MOD, EXP, AND, OR, NOT, E_NOT, EQ, NE, LT, GT, GOARROW1, GOARROW2, RETARROW1, RETARROW2, ARROW_SHAFT, NOJUMP, COMMA, COLON, CAST, SEMICOLON, PARAM, LPAREN, RPAREN, LBRAK, RBRAK, LCURLY, RCURLY, INT, FLOAT, BOOL, STRING, ARRAY, LIST, NULL, NUMBER, RAW_STRING, BOOLEAN, IDENT, ARG, VAR, SET, GOTO, IF, COMPARE, PRINT, READ, DELETE, TRY, INCLUDE, RETURN, QUIT, USRFUNC, TYPE, LABEL, LEN, EOF, getSym, mark
import bc2_1_st as ST
from bc2_1_st import newJmp, setSpc, setUsr
import bc2_1_e as E
from bc2_1_e import Variable, Collection

calls = 0

def call(production):
    def wrapper():
        global calls
        calls += 1
        production()
    return wrapper

FIRSTPRIMATIVE  = {INT, FLOAT, BOOL, STRING, NULL}
FOLLOWPRIMATIVE = FIRSTPRIMATIVE

FIRSTCOLLECTION  = {ARRAY, LIST}
FOLLOWCOLLECTION = FIRSTCOLLECTION

FIRSTARROW  = {GOARROW1, GOARROW2, RETARROW1, RETARROW2}
FOLLOWARROW = FIRSTARROW

FIRSTLABEL  = {IDENT, GOARROW1, GOARROW2, RETARROW1, RETARROW2, ARROW_SHAFT, NOJUMP}
FOLLOWLABEL = FIRSTLABEL

FIRSTINDEX  = {LBRAK}
FOLLOWINDEX = {RBRAK}

FIRSTFUNC  = {TYPE, LABEL, LEN}
FOLLOWFUNC = FIRSTFUNC

FIRSTFULL_TYPE  = FIRSTPRIMATIVE
FOLLOWFULL_TYPE = FOLLOWPRIMATIVE | FOLLOWCOLLECTION

FIRSTCAST_TYPE  = {CAST}
FOLLOWCAST_TYPE = FOLLOWFULL_TYPE

FIRSTATOM  = {NUMBER, IDENT, RAW_STRING, BOOLEAN, LPAREN, LCURLY} | FIRSTFUNC
FOLLOWATOM = FOLLOWINDEX | {NUMBER, IDENT, RAW_STRING, BOOLEAN, RPAREN, RCURLY} | FOLLOWCAST_TYPE # FOLLOWCAST_TYPE is from SUBATOM

FIRSTSUBATOM  = FIRSTATOM
FOLLOWSUBATOM = FOLLOWATOM | FOLLOWCAST_TYPE

FIRSTEXPR_L7 = FIRSTSUBATOM | {NOT}
FOLLOWEXPR_L7 = FOLLOWSUBATOM

FIRSTEXPR_L6 = FIRSTEXPR_L7
FOLLOWEXPR_L6 = FOLLOWSUBATOM

FIRSTEXPR_L5 = FIRSTEXPR_L7
FOLLOWEXPR_L5 = FOLLOWSUBATOM

FIRSTEXPR_L4 = FIRSTEXPR_L7 | {PLUS, MINUS}
FOLLOWEXPR_L4 = FOLLOWSUBATOM

FIRSTEXPR_L3 = FIRSTEXPR_L4
FOLLOWEXPR_L3 = FOLLOWSUBATOM

FIRSTEXPR_L2 = FIRSTEXPR_L4
FOLLOWEXPR_L2 = FOLLOWSUBATOM

FIRSTEXPR_L1 = FIRSTEXPR_L4
FOLLOWEXPR_L1 = FOLLOWSUBATOM

FIRSTEXPR = FIRSTEXPR_L4 | {E_NOT}
FOLLOWEXPR = FOLLOWSUBATOM

FIRSTSTMT  = {VAR, SET, GOTO, IF, COMPARE, PRINT, READ, DELETE, TRY, INCLUDE, QUIT} #, RETURN}
FOLLOWSTMT = FOLLOWEXPR | FOLLOWLABEL | FOLLOWCAST_TYPE | {IDENT, RAW_STRING}

FIRSTLINE  = FIRSTSTMT
FOLLOWLINE = {SEMICOLON}

FIRSTPROGRAM  = FIRSTARROW | FIRSTLINE | {IDENT}
FOLLOWPROGRAM = FOLLOWLINE

@call
def program():
    if SC.sym not in FIRSTPROGRAM | {EOF}: mark('incorrect start: program')

    ST.setSpc(GOARROW1, SC.line) # Very beginning is jumpable
    ST.setSpc(GOARROW2, SC.line)

    while SC.sym in FIRSTPROGRAM:
        while SC.sym in FIRSTARROW:
            arrow()
        if SC.sym == IDENT:
            name = SC.val
            getSym()
            if SC.sym == COLON:
                ST.newJmp(name, SC.line); getSym()
            else:
                mark('expected colon')

        if SC.sym in FIRSTLINE:
            line()

    ST.setSpc(RETARROW1, SC.line) # Very end is jumpable
    ST.setSpc(RETARROW2, SC.line)

@call
def arrow():
    if SC.sym not in FIRSTARROW: mark('invalid start: arrow')

    if SC.sym == GOARROW1:
        ST.setSpc(GOARROW1, SC.line); getSym();
    elif SC.sym == GOARROW2:
        ST.setSpc(GOARROW2, SC.line); getSym();
    elif SC.sym == RETARROW1:
        ST.setSpc(RETARROW1, SC.line); getSym();
    elif SC.sym == RETARROW2:
        ST.setSpc(RETARROW2, SC.line); getSym();
    else: mark('invalid switch symbol: arrow')

@call
def line():
    if SC.sym not in FIRSTLINE: mark('invalid start: line')

    stmt()

    if SC.sym != SEMICOLON:
        mark('missing semicolon')
        while SC.sym not in FOLLOWLINE:
            getSym()
    getSym()

@call
def stmt():
    if SC.sym not in FIRSTSTMT: mark('invalid start: stmt')

    if SC.sym == VAR:
        getSym()
        if SC.sym == IDENT:             getSym()
        else:                           mark('expected identifier')

        if SC.sym in FIRSTCAST_TYPE:    cast_type()
        else:                           mark('expected type cast')

        if SC.sym in FIRSTEXPR:         expr()
        # else:                           mark('expected expression')

    elif SC.sym == SET:
        getSym()
        if SC.sym == IDENT:     getSym()
        else:                   mark('expected identifier')

        if SC.sym in FIRSTEXPR: expr()
        else:                   mark('expected expression')

    elif SC.sym == GOTO:
        getSym()
        if SC.sym in FIRSTLABEL:    label()
        else:                       mark('expected label')

    elif SC.sym == IF:
        getSym()
        if SC.sym in FIRSTEXPR:     expr()
        else:                       mark('expected expression')

        if SC.sym in FIRSTLABEL:    label()
        else:                       mark('expected label')

    elif SC.sym == COMPARE:
        getSym()
        if SC.sym in FIRSTEXPR: expr()
        else:                   mark('expected expression')

        # if SC.sym in FIRSTLABEL:
        #     mark('compare statement does not take jump locations')

    elif SC.sym == PRINT:
        getSym()
        if SC.sym in FIRSTEXPR: expr()
        else:                   mark('expected expression')

    elif SC.sym == READ:
        getSym()
        if SC.sym == IDENT:             getSym()
        else:                           mark('expected identifier')

        if SC.sym in FIRSTCAST_TYPE:    cast_type()
        else:                           mark('expected type cast')

    elif SC.sym == DELETE:
        getSym()
        if SC.sym == IDENT: getSym()
        else:               mark('expected identifier')

    elif SC.sym == TRY:
        getSym()

        if SC.sym in FIRSTSTMT:     stmt()
        else:                       mark('expected statement')

        if SC.sym in FIRSTLABEL:    label()
        else:                       mark('expected label')

    elif SC.sym == INCLUDE:
        getSym()

        if SC.sym == IDENT:
            #SC.usrfunc.append(SC.val)
            setUsr(SC.val,USRFUNC)
            getSym()
        else: mark('expected identifier')

    # elif SC.sym == RETURN:
    #     getSym()
    #     if SC.sym not in FOLLOWLINE:
    #         mark('ret statement takes no arguments')
    #         while SC.sym not in FOLLOWLINE:
    #             getSym()

    elif SC.sym == QUIT:
        getSym()
        if SC.sym not in FOLLOWLINE:
            mark('quit statement takes no arguments')
            while SC.sym not in FOLLOWLINE:
                getSym()

    else: mark('invalid switch symbol: stmt')

@call
def label():
    if SC.sym not in FIRSTLABEL: mark('invalid start: label')

    if SC.sym == IDENT:
        getSym()
    elif SC.sym == RETARROW1:
        getSym()
        while SC.sym == ARROW_SHAFT: getSym()
    elif SC.sym == RETARROW2:
        getSym()
        while SC.sym == ARROW_SHAFT: getSym()
    elif SC.sym == GOARROW1:
        getSym()
    elif SC.sym == GOARROW2:
        getSym()
    elif SC.sym == ARROW_SHAFT:
        while SC.sym == ARROW_SHAFT: getSym()
        if SC.sym == GOARROW1: getSym()
        elif SC.sym == GOARROW2: getSym()
        else: mark('expected arrowhead')
    elif SC.sym == NOJUMP:
        getSym()
    else: mark('invalid switch symbol: label')

@call
def cast_type():
    if SC.sym not in FIRSTCAST_TYPE: mark('invalid start: cast_type')

    if SC.sym == CAST: getSym()
    else: mark('expected cast')

    if SC.sym in FIRSTFULL_TYPE:
        full_type()
    # Error Handling - Collection type is given first
    elif SC.sym in FIRSTCOLLECTION:
        mark('primitive type must come before collection type')
        getSym()
    # Error Handling - Using literal as cast
    elif SC.sym in FIRSTEXPR:
        mark('operands cannot be used as casts')
        while SC.sym not in FOLLOWEXPR:
            getSym()
    else: mark('expected type')

@call
def full_type():
    if SC.sym not in FIRSTFULL_TYPE: mark('invalid start: full_type')

    if SC.sym in FIRSTPRIMATIVE:
        primative()
    else: mark('expected primative')

    if SC.sym == CAST:
        getSym()
        if SC.sym in FIRSTCOLLECTION:
            collection()
        else: mark('expected collection')
    # Error Handling - Accidentally using single colon instead of the cast operator -> Requires lookahead
    # elif SC.sym == COLON:
    #     mark('cast operator must be used for casting'); raise Exception()
    #     while SC.sym in {COLON} | FIRSTPRIMATIVE | FIRSTCOLLECTION:
    #         getSym()

@call
def expr():
    if SC.sym not in FIRSTEXPR: mark('invalid start: expr')

    if SC.sym == E_NOT: getSym()
    expr_l1()

@call
def expr_l1():
    if SC.sym not in FIRSTEXPR_L1: mark('invalid start: expr_l1')

    expr_l2()
    while SC.sym == OR:
        getSym()
        if SC.sym in FIRSTEXPR_L1:
            expr_l2()
        else:
            # Error Handling - Missing operand
            mark('expected expression')
            while SC.sym not in FOLLOWEXPR_L1 | FOLLOWLINE | FIRSTLABEL:
                getSym()

@call
def expr_l2():
    if SC.sym not in FIRSTEXPR_L2: mark('invalid start: expr_l2')

    expr_l3()
    while SC.sym == AND:
        getSym()
        if SC.sym in FIRSTEXPR_L2:
            expr_l3()
        else:
            # Error Handling - Missing operand
            mark('expected expression')
            while SC.sym not in FOLLOWEXPR_L2 | FOLLOWLINE | FIRSTLABEL:
                getSym()

@call
def expr_l3():
    if SC.sym not in FIRSTEXPR_L3: mark('invalid start: expr_l3')

    expr_l4()
    while SC.sym in {EQ, NE, LT, GT}:
        getSym()
        if SC.sym in FIRSTEXPR_L3:
            expr_l4()
        else:
            # Error Handling - Missing operand
            mark('expected expression')
            while SC.sym not in FOLLOWEXPR_L3 | FOLLOWLINE | FIRSTLABEL:
                getSym()

@call
def expr_l4():
    if SC.sym not in FIRSTEXPR_L4: mark('invalid start: expr_l4')

    if SC.sym == PLUS: getSym()
    elif SC.sym == MINUS: getSym()

    expr_l5()
    while SC.sym in {PLUS, MINUS}:
        getSym()
        if SC.sym in FIRSTEXPR_L5:
            expr_l5()
        else:
            # Error Handling - Missing operand
            mark('expected expression')
            while SC.sym not in FOLLOWEXPR_L5 | FOLLOWLINE | FIRSTLABEL:
                getSym()

@call
def expr_l5():
    if SC.sym not in FIRSTEXPR_L5: mark('invalid start: expr_l5')

    expr_l6()
    while SC.sym in {MULT, DIV, MOD}:
        getSym()
        if SC.sym in FIRSTEXPR_L5:
            expr_l6()
        else:
            # Error Handling - Missing operand
            mark('expected expression')
            while SC.sym not in FOLLOWEXPR_L5 | FOLLOWLINE | FIRSTLABEL:
                getSym()

@call
def expr_l6():
    if SC.sym not in FIRSTEXPR_L6: mark('invalid start: expr_l6')

    expr_l7()
    if SC.sym == EXP:
        getSym()
        if SC.sym in FIRSTEXPR_L6:
            expr_l7()
        else:
            # Error Handling - Missing operand
            mark('expected expression')
            while SC.sym not in FOLLOWEXPR_L6 | FOLLOWLINE | FIRSTLABEL:
                getSym()

@call
def expr_l7():
    if SC.sym not in FIRSTEXPR_L7: mark('invalid start: expr_l7')

    if SC.sym == NOT: getSym()
    subatom()

@call
def subatom():
    if SC.sym not in FIRSTSUBATOM: mark('invalid start: subatom')

    atom()

    # Error Handling - type is not cast, but just stated
    if SC.sym in FIRSTPRIMATIVE | FIRSTCOLLECTION:
        mark('operands must be cast to types')
        while SC.sym in FIRSTPRIMATIVE | FIRSTCOLLECTION:
            getSym()

    while SC.sym in FIRSTCAST_TYPE:
        cast_type()

@call
def atom():
    if SC.sym not in FIRSTATOM: mark('invalid start: atom')

    if SC.sym == NUMBER:
        getSym()

    elif SC.sym == RAW_STRING:
        getSym()
        if SC.sym in FIRSTINDEX:
            index()

    elif SC.sym == BOOLEAN:
        getSym()

    elif SC.sym == LPAREN:
        getSym()
        expr()
        if SC.sym == RPAREN: getSym()
        # Error Handling - No closing bracket
        else:
            mark('expected closing parenthesis')
            while SC.sym not in {RPAREN} | FOLLOWLINE:
                getSym()

    elif SC.sym == LCURLY:
        getSym()
        # Error Handling - Accidentally casting type
        if SC.sym == CAST: mark('collections require declarations, not casting'); getSym()

        if SC.sym in FIRSTFULL_TYPE:
            full_type()
        # Error handling - Missing type declaration
        elif SC.sym in FIRSTEXPR:
            mark('collections require type declaration after curly brace')
            while SC.sym not in FIRSTFULL_TYPE | FOLLOWLINE | FIRSTEXPR:
                getSym()
        # Error Handling - Casting to collection
        elif SC.sym in FIRSTCOLLECTION:
            mark('missing primative type')
            while SC.sym in FIRSTCOLLECTION:
                getSym()
        else: mark('expected type')

        # Error Handling - More than one primitive or collection type
        # Error Handling - Using colon instead of cast operator -> requires lookahead
        if SC.sym in {CAST}:
            if SC.sym == CAST: mark('collections only accept 1 primative and collection type ')
            # elif SC.sym == COLON: mark('cast operator must be used for casting type '); getSym()
            while SC.sym in {CAST} | FIRSTPRIMATIVE | FIRSTCOLLECTION:
                getSym()

        if SC.sym == COLON: getSym()
        else: mark('expected colon')

        expr()

        if SC.sym == COMMA:
            while SC.sym == COMMA:
                getSym()
                expr()

            # Error Handling - try to define range and elements
            if SC.sym == COLON:
                mark('must define range or elements')
                while SC.sym not in {RCURLY} | FOLLOWLINE:
                    getSym()

        elif SC.sym == COLON:
            getSym()
            expr()

            # Error Handling - try to define range and elements
            if SC.sym == COMMA:
                mark('must define range or elements')
                while SC.sym not in {RCURLY} | FOLLOWLINE:
                    getSym()

        else: mark('invalid switch symbol: atom - set')

        if SC.sym == RCURLY: getSym()
        else:
            mark('expected closing curly brace')
            while SC.sym in {RCURLY} | FOLLOWLINE:
                getSym()

    # elif SC.sym == IDENT:
    #     getSym()
    #     if SC.sym in FIRSTINDEX:
    #         index()

    elif SC.sym in FIRSTFUNC | {IDENT}:
        if SC.val in ST.usrTab[-1] or SC.sym in FIRSTFUNC:
            # Function
            func()

            while SC.sym == PARAM:
                getSym()

                if SC.sym in FIRSTEXPR:
                    expr()
                else:
                    # Error Handling - Non-expression argument
                    mark('arguments must be expressions')
                    while SC.sym not in {PARAM} | FOLLOWEXPR | FOLLOWLINE:
                        getSym()

            # Error Handling - Forgot the param operator
            if SC.sym in FIRSTEXPR:
                mark('arguments require parameter operator')
                while SC.sym not in {PARAM} | FIRSTEXPR | FOLLOWEXPR:
                    getSym() # Eat all args

        else:
            # Identifier

            getSym()
            if SC.sym in FIRSTINDEX:
                index()

            # Error Handling - Ensure param isnt accidentally used - Requires lookbehind
            # elif SC.sym == PARAM:
            #     mark('function not defined')
            #     while SC.sym not in FOLLOWLINE:
            #         getSym()


    else: mark('invalid switch symbol: atom')

@call
def index():
    if SC.sym not in FIRSTINDEX: mark('invalid start: index')

    if SC.sym == LBRAK: getSym()
    else: mark('expected opening brace')

    expr()

    if SC.sym == RBRAK: getSym()
    else: mark('expected closing brace')

    # Error handling - A double index is attempted
    if SC.sym in FIRSTINDEX:
        mark('only one dimensional objects are legal')
        while SC.sym not in FOLLOWLINE:
            getSym()

@call
def primative():
    if SC.sym not in FIRSTPRIMATIVE: mark('invalid start: primative')

    if SC.sym == INT: getSym()
    elif SC.sym == FLOAT: getSym()
    elif SC.sym == BOOL: getSym()
    elif SC.sym == STRING: getSym()
    elif SC.sym == NULL: getSym()
    else: mark('invalid switch symbol: primative')

@call
def collection():
    if SC.sym not in FIRSTCOLLECTION: mark('invalid start: collection')

    if SC.sym == ARRAY: getSym()
    elif SC.sym == LIST: getSym()
    else: mark('invalid switch symbol: collection')

@call
def func():
    if SC.sym not in FIRSTFUNC | {IDENT}: mark('invalid start: func')

    if SC.sym == TYPE: getSym()
    elif SC.sym == LABEL: getSym()
    elif SC.sym == LEN: getSym()
    elif SC.sym == IDENT: getSym()
    else: mark('invalid switch symbol: func')

def execute():
    program()
    # if not SC.error:    print('No errors detected')
    # else:               print('Errors found')

def execute_debug():
    # Expects SC to be initialized, ST to be made
    global calls
    from time import time

    # Initialize
    calls = 0

    start = time()
    program()
    end = time()

    print("=GRAMMAR=")
    print(end-start,end='s\n')
    print('Calls:',calls)
    # ST.printTab()
    if SC.error:    print('error during preprocessing')
    else:           print('no grammar errors')
    print()


if __name__ == '__main__':
    src = ''
    with open('usr.ngl','r') as reader:
        for src_line in reader.readlines():
            src += src_line

    _execute(src)
