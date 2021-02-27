# NGL Bytecode 3.0 Grammar Skeleton

from bc3_scanner import Scanner
from bc3_scanner import ENOT, PARAM, OR, UNION, AND, INTER, EQ, NE, LT, GT, PLUS, MINUS, MULT, DIV, INTDIV, MOD, EXP, NOT, CAST, VAR, CONST, READ, SET, DEL, GOTO, IF, TRY, EXEC, PRINT, INCLUDE, QUIT, RETURN, LOG, GOARROW1, GOARROW2, RETARROW1, RETARROW2, ARROWSHAFT, NOJUMP, LPAREN, RPAREN, LBRAK, RBRAK, LCURLY, RCURLY, COMMA, COLON, INT, FLOAT, STR, BOOL, ARRAY, LIST, FUNC, LABEL, NONE, NUMBER, DECIMAL, STRING, IDENT, LINEEND, NEWLINE, EOF, ARROWS, TYPES
from bc3_scanner import FIRST_LABEL, LAST_LABEL, FIRST_TYPE, LAST_TYPE, FIRST_CAST, LAST_CAST, FIRST_LINEEND, LAST_LINEEND, FIRST_ATOM, LAST_ATOM, FIRST_SUBATOM, LAST_SUBATOM, FIRST_EXPR_L9, LAST_EXPR_L9, FIRST_EXPR_L8, LAST_EXPR_L8, FIRST_EXPR_L7, LAST_EXPR_L7, FIRST_EXPR_L6, LAST_EXPR_L6, FIRST_EXPR_L5, LAST_EXPR_L5, FIRST_EXPR_L4, LAST_EXPR_L4, FIRST_EXPR_L3, LAST_EXPR_L3, FIRST_EXPR_L2, LAST_EXPR_L2, FIRST_EXPR_S2, LAST_EXPR_S2, FIRST_EXPR_L1, LAST_EXPR_L1, FIRST_EXPR_S1, LAST_EXPR_S1, FIRST_EXPR_L0, LAST_EXPR_L0, FIRST_EXPR, LAST_EXPR, FIRST_STMT, LAST_STMT, FIRST_LINE, LAST_LINE, FIRST_PROG, LAST_PROG
import bc3_symboltable as ST

from bc3_logging import getLogger
from bc3_data import Int, Float, Str, Bool, Func, Lab, Ref, Array, List

# TODO: update logging to inform of check results

missing = []

def prog():
    global SC
    if SC.sym not in FIRST_PROG:
        SC.mark('attempt to parse {0} as PROG'.format(SC.sym))

    while SC.sym in FIRST_LINE:
        line()

def line():
    global SC
    if SC.sym not in FIRST_LINE:
        SC.mark('attempt to parse {0} as LINE'.format(SC.sym))

    while SC.sym in ARROWS:
        ST.setSpc(SC.sym,SC.line)
        gra_logger.info('added to arrow {0} jump with {1}'.format(SC.sym,SC.line))
        SC.getSym()

    if SC.sym == IDENT:
        ST.newSym(SC.val,Lab(SC.line))
        gra_logger.info('label {0} jump to {1}'.format(SC.val,SC.line))
        SC.getSym()
        if SC.sym == COLON: SC.getSym()
        else:               SC.mark('expected colon')

    if SC.sym in FIRST_STMT:
        stmt()

    lineend()

def label():
    global SC
    if SC.sym not in FIRST_LABEL:
        SC.mark('attempt to parse {0} as LABEL'.format(SC.sym))

    if SC.sym in ({ARROWSHAFT,GOARROW1,GOARROW2}):
        while SC.sym == ARROWSHAFT: SC.getSym()

        if SC.sym in set({GOARROW1,GOARROW2}):
            SC.getSym()
        else:
            SC.mark('expected arrow')

    elif SC.sym in set({RETARROW1,RETARROW2}):
        SC.getSym()
        while SC.sym == ARROWSHAFT: SC.getSym()

    elif SC.sym == NOJUMP:
        SC.getSym()

    elif SC.sym == IDENT:
        SC.getSym()

    else:
        SC.mark('expected label, got {0}'.format(SC.sym))

def stmt():
    global SC, missing
    if SC.sym not in FIRST_STMT:
        SC.mark('attempt to parse {0} as STMT'.format(SC.sym))

    if SC.sym == VAR:
        # TODO: log var, type and val if present
        SC.getSym()

        if SC.sym == IDENT:         name = SC.val; SC.getSym()
        else:                       SC.mark('expected identifier')

        if SC.sym == CAST:          SC.getSym()

        if SC.sym in FIRST_TYPE:    varType = typ();
        else:                       SC.mark('expected type')

        if SC.sym in FIRST_EXPR:
            exprType = expr()

            # if type(exprType) == Ref and ST.hasSym(exprType.data):
            #     exprType = ST.getSym(exprType.data)

            if varType != exprType:
                SC.mark('variable type mismatch',logger=gra_logger)

            if type(varType) == Ref and varType.type == 'func' and type(exprType) == Func:
                varType = Func(exprType.val)
            elif type(varType) == Ref and varType.type == 'label' and type(exprType) == Lab:
                varType = Lab(exprType.val)

        if type(varType) == Ref and varType.type == 'ident':
            missing.append(name)

        ST.newSym(name,varType)

    elif SC.sym == CONST:
        # TODO: log var, type and val if present
        SC.getSym()

        if SC.sym == IDENT:         name = SC.val; SC.getSym()
        else:                       SC.mark('expected identifier')

        if SC.sym == CAST:          SC.getSym()

        if SC.sym in FIRST_TYPE:  constType = typ(); # TODO: update other docs to be consistent
        else:                       SC.mark('expected type')

        if SC.sym in FIRST_EXPR:    exprType = expr()
        else:                       SC.mark('expected expression, got {0}'.format(SC.sym))

        if type(constType) == Ref and constType.type == 'func' and type(exprType) == Func:
            constType = Func(exprType.val)
        elif type(constType) == Ref and constType.type == 'label' and type(exprType) == Lab:
            constType = Lab(exprType.val)

        if constType != exprType:
            SC.mark('variable type mismatch {0}'.format(name),logger=gra_logger)

        if type(constType) == Ref and constType.type == 'ident':
            missing.append(name)

        constType.const = True
        ST.newSym(name,constType)

    elif SC.sym == READ:
        # TODO: log var, val and if created new var
        SC.getSym()

        if SC.sym == IDENT:         name = SC.val; SC.getSym()
        else:                       SC.mark('expected identifier')

        if SC.sym in FIRST_EXPR:    exprType = expr(); ST.newSym(name,exprType)
        else:                       ST.newSym(name,Ref('input'))

        # create new var or load existing var
        ST.newSym(name,exprType) # FIX

    elif SC.sym == SET:
        # TODO: log var and val
        SC.getSym()

        if SC.sym == IDENT:         name = SC.val; SC.getSym() # TODO: find type
        else:                       SC.mark('expected identifier')

        if SC.sym in FIRST_EXPR:    exprType = expr()
        else:                       SC.mark('expected expression')

        if not ST.hasSym(name):
            SC.mark('variable {0} does not exist'.format(name),logger=gra_logger)

        else:
            varType = ST.getSym(name)

            if varType.const:
                SC.mark('constant value cannot be reassigned',logger=gra_logger)

            else:
                if varType != exprType:
                    SC.mark('variable type mismatch {0}'.format(name),logger=gra_logger)

                if type(exprType) == Ref and exprType.type == 'ident':
                    missing.append(name)

                ST.setSym(name,exprType)

    elif SC.sym == DEL:
        SC.getSym()

        if SC.sym == IDENT:         name = SC.val; SC.getSym()
        else:                       SC.mark('expected identifier')

        # if constType != exprType:
        #     SC.mark('type mismatch',logger=gra_logger)

        if ST.hasSym(name): ST.delSym(name)
        else:               SC.mark('non-existant identifier',logger=gra_logger)

    elif SC.sym == GOTO:
        SC.getSym()

        if SC.sym in FIRST_LABEL:   label()
        else:                       SC.mark('expected label')

    elif SC.sym == IF:
        SC.getSym()

        if SC.sym in FIRST_EXPR:    exprType = expr()
        else:                       SC.mark('expected expression')

        if type(exprType) != Bool:
            SC.mark('expected boolean result',logger=gra_logger)

        if SC.sym in FIRST_LABEL:   label()
        else:                       SC.mark('expected label')

    elif SC.sym == EXEC:
        SC.getSym()

        if SC.sym in FIRST_EXPR:    expr()
        else:                       SC.mark('expected expression')

    elif SC.sym == TRY:
        SC.getSym()

        if SC.sym in FIRST_STMT:    stmt()
        else:                       SC.mark('expected statement')

        if SC.sym in FIRST_LABEL:   label()
        else:                       SC.mark('expected label')

    elif SC.sym == PRINT:
        SC.getSym()

        if SC.sym in FIRST_EXPR:    exprType = expr()
        else:                       SC.mark('expected expression')

        if type(exprType) != Str:
            SC.mark('expected str result',logger=gra_logger)

    elif SC.sym == INCLUDE:
        SC.getSym()

        if SC.sym == IDENT:         name = SC.val; SC.getSym()
        else:                       SC.mark('expected identifier')

        ST.newSym(name,Func('{0}.ngl'.format(name)))

    elif SC.sym == QUIT:
        SC.getSym()

    elif SC.sym == RETURN:
        SC.getSym()

    elif SC.sym == LOG:
        SC.getSym()

        if SC.sym == FIRST_EXPR:    exprType = expr()
        else:                       SC.mark('expected identifier')

        if type(exprType) != Str:
            SC.mark('expected str result',logger=gra_logger)

def expr():
    if SC.sym not in FIRST_EXPR:
        SC.mark('attempt to parse {0} as EXPR'.format(SC.sym))

    inv = False
    if SC.sym == ENOT:  SC.getSym(); inv = True

    base = expr_l0()

    if inv:
        if type(base) != Bool:
            SC.mark('only booleans can take expression negation',logger=gra_logger)
        base = Bool()

    return base

def expr_l0():
    if SC.sym not in FIRST_EXPR_L0:
        SC.mark('attempt to parse {0} as EXPR_L0'.format(SC.sym))

    base = expr_s1()

    if SC.sym == PARAM:
        SC.getSym()
        sub = expr()
        while SC.sym == COMMA:
            SC.getSym()
            sub = expr()

        base = Ref('func')

    return base

def expr_s1():
    if SC.sym not in FIRST_EXPR_S1:
        SC.mark('attempt to parse {0} as EXPR_S1'.format(SC.sym))

    base = expr_l1()

    if SC.sym in set({OR}):
        if type(base) not in set({Bool}):
            SC.mark('only boolean types can take logical or',logger=gra_logger)

        while SC.sym in set({OR}):
            SC.getSym()

            mod = expr_l1()

            if type(base) not in set({Bool}):
                SC.mark('only boolean types can take logical or',logger=gra_logger)

        base = Bool()

    return base

def expr_l1():
    if SC.sym not in FIRST_EXPR_L1:
        SC.mark('attempt to parse {0} as EXPR_L1'.format(SC.sym))

    base = expr_s2()

    if SC.sym in set({AND}):
        if type(base) not in set({Bool}):
            SC.mark('only boolean types can take logical and',logger=gra_logger)

        while SC.sym in set({AND}):
            SC.getSym()

            mod = expr_s2()

            if type(base) not in set({Bool}):
                SC.mark('only boolean types can take logical and',logger=gra_logger)

        base = Bool()

    return base

def expr_s2():
    if SC.sym not in FIRST_EXPR_S2:
        SC.mark('attempt to parse {0} as EXPR_S2'.format(SC.sym))

    base = expr_l2()

    if SC.sym in set({UNION}):
        if type(base) not in set({Array,List}):
            SC.mark('only collection types can take union',logger=gra_logger)

        while SC.sym in set({UNION}):
            SC.getSym()

            mod = expr_l2()

            if type(base) not in set({Array,List}):
                SC.mark('only collection types can take union',logger=gra_logger)

        base = List(base.type)

    return base

def expr_l2():
    if SC.sym not in FIRST_EXPR_L2:
        SC.mark('attempt to parse {0} as EXPR_L2'.format(SC.sym))

    base = expr_l3()

    if SC.sym in set({INTER}):
        if type(base) not in set({Array,List}):
            SC.mark('only collection types can take intersection',logger=gra_logger)

        while SC.sym in set({INTER}):
            SC.getSym()

            mod = expr_l3()

            if type(base) not in set({Array,List}):
                SC.mark('only collection types can take intersection',logger=gra_logger)

        base = List(base.type)

    return base

def expr_l3():
    if SC.sym not in FIRST_EXPR_L3:
        SC.mark('attempt to parse {0} as EXPR_L3'.format(SC.sym))

    base = expr_l4()

    if SC.sym in set({EQ,NE}):

        while SC.sym in set({EQ,NE}):
            SC.getSym()

            mod = expr_l4()

        base = Bool()

    return base

def expr_l4():
    if SC.sym not in FIRST_EXPR_L4:
        SC.mark('attempt to parse {0} as EXPR_L4'.format(SC.sym))

    base = expr_l5()

    if SC.sym in set({LT,GT}):
        if type(base) in set({Array,List}):
            SC.mark('collection type cannot take relational operators',logger=gra_logger)
        elif type(base) in set({Bool}):
            SC.mark('boolean cannot take relational operators',logger=gra_logger)

        while SC.sym in set({LT,GT}):
            SC.getSym()

            mod = expr_l5()

            if type(mod) in set({Bool}):
                SC.mark('boolean cannot take additive operators',logger=gra_logger)
            elif type(mod) in set({Array,List}):
                SC.mark('collection type cannot take additive operators',logger=gra_logger)

        base = Bool()

    return base

def expr_l5():
    if SC.sym not in FIRST_EXPR_L5:
        SC.mark('attempt to parse {0} as EXPR_L5'.format(SC.sym))

    base = expr_l6()

    if SC.sym in set({PLUS,MINUS}):
        if type(base) in set({Array,List}):
            SC.mark('collection type cannot take additive operators',logger=gra_logger)
        elif type(base) not in set({Int,Float}):
            SC.mark('only numerical types can take additive operators',logger=gra_logger)

        while SC.sym in set({PLUS,MINUS}):
            SC.getSym()

            mod = expr_l6()

            if type(mod) in set({Array,List}):
                SC.mark('collection type cannot take additive operators',logger=gra_logger)
            elif type(mod) in set({Str,Bool}):
                SC.mark('only numerical types can take additive operators',logger=gra_logger)

            if type(base) == Int and type(mod) == Float:
                base = Float()

    return base

def expr_l6():
    if SC.sym not in FIRST_EXPR_L6:
        SC.mark('attempt to parse {0} as EXPR_L6'.format(SC.sym))

    base = expr_l7()

    if SC.sym in set({MULT,DIV,INTDIV,MOD}):
        if type(base) in set({Array,List}):
            SC.mark('collection type cannot take multiplicative operators',logger=gra_logger)
        elif type(base) not in set({Int,Float}):
            SC.mark('only numerical types can take multiplicative operators',logger=gra_logger)

        while SC.sym in set({MULT,DIV,INTDIV,MOD}):
            SC.getSym()

            mod = expr_l7()

            if type(mod) in set({Array,List}):
                SC.mark('collection type cannot take multiplicative operators',logger=gra_logger)
            elif type(mod) not in set({Int,Float}):
                SC.mark('only numerical types can take multiplicative operators',logger=gra_logger)

            if type(base) == Int and type(mod) == Float:
                base = Float()

    return base

def expr_l7():
    if SC.sym not in FIRST_EXPR_L7:
        SC.mark('attempt to parse {0} as EXPR_L7'.format(SC.sym))

    base = expr_l8()

    if SC.sym == EXP:
        if type(base) in set({Array,List}):
            SC.mark('collection type cannot take exponentiation',logger=gra_logger)
        elif type(base) not in set({Int,Float}):
            SC.mark('only numerical types can take exponentiation',logger=gra_logger)

        while SC.sym == EXP:
            SC.getSym()

            mod = expr_l8()

            if type(mod) in set({Array,List}):
                SC.mark('collection type cannot take exponentiation',logger=gra_logger)
            elif type(mod) in set({Str,Bool}):
                SC.mark('only numerical types can take exponentiation',logger=gra_logger)

            if type(base) == Int and type(mod) == Float:
                base = Float()

    return base

def expr_l8():
    if SC.sym not in FIRST_EXPR_L8:
        SC.mark('attempt to parse {0} as EXPR_L8'.format(SC.sym))

    op = None
    if SC.sym == PLUS:      op = SC.sym; SC.getSym()
    elif SC.sym == MINUS:   op = SC.sym; SC.getSym()
    elif SC.sym == NOT:     op = SC.sym; SC.getSym()

    base = expr_l9()

    if type(base) in (Array,List):  sub = base.type
    else:                           sub = base

    if op == PLUS and type(base) not in set({Int,Float}):
        SC.mark('only numerical types can take unary addition',logger=gra_logger)
    elif op == MINUS and type(base) not in set({Int,Float}):
        SC.mark('only numerical types can take unary subtraction',logger=gra_logger)
    elif op == PLUS and type(base) not in set({Bool}):
        SC.mark('only booleans can take logical not',logger=gra_logger)

    return base

def expr_l9():
    if SC.sym not in FIRST_EXPR_L9:
        SC.mark('attempt to parse {0} as EXPR_L9'.format(SC.sym))

    base = subatom()

    if SC.sym == CAST:
        SC.getSym()
        base = typ()

    return base

def subatom():
    if SC.sym not in FIRST_SUBATOM:
        SC.mark('attempt to parse {0} as SUBATOM'.format(SC.sym))

    base = atom()

    if SC.sym == LBRAK:
        # Int, Float can be indexed for digits, string for chars
        if type(base) not in set({Int,Float,Str,Array,List}):
            SC.mark('type cannot be indexed',logger=gra_logger)

        SC.getSym()
        sub = expr()

        if type(sub) != Int:
            SC.mark('index must be integer',logger=gra_logger)

        if SC.sym == RBRAK: SC.getSym()
        else:               SC.mark('expected closing bracket')

    return base

def atom():
    if SC.sym not in FIRST_ATOM:
        SC.mark('attempt to parse {0} as ATOM'.format(SC.sym))

    if SC.sym == NUMBER:
        SC.getSym()
        base = Int()

    elif SC.sym == DECIMAL:
        SC.getSym()
        base = Float()

    elif SC.sym == IDENT:
        name = SC.val
        SC.getSym()
        if ST.hasSym(name): base = ST.getSym(name)
        else:               base = Ref('ident')
        # TODO: base = ??
        # IDEA: For proper parser, return a 'Variable' object which only gets looked up when needed

    elif SC.sym == STRING:
        SC.getSym()
        base = Str()

    elif SC.sym == LPAREN:
        SC.getSym()

        base = expr()
        if SC.sym == RPAREN:    SC.getSym()
        else:                   SC.mark('expected closing parenthesis')

    elif SC.sym == LCURLY:
        SC.getSym()

        base = typ()

        if type(base) not in (Array, List):
            SC.mark('expected collection type',logger=gra_logger)

        if SC.sym == COLON:     SC.getSym()
        else:                   SC.mark('expected colon')

        if SC.sym in FIRST_EXPR:
            sub = expr() # subtype

            if SC.sym == COMMA:

                if base.type != sub:
                    SC.mark('collection-element type mismatch',logger=gra_logger)

                while SC.sym == COMMA:
                    SC.getSym()
                    sub = expr()

                    if base.type != sub:
                        SC.mark('collection-element type mismatch',logger=gra_logger)

            elif SC.sym == COLON:
                SC.getSym()

                if type(sub) != Int:
                    SC.mark('lower bound must be integer',logger=gra_logger)

                top = expr()

                if type(top) != Int:
                    SC.mark('upper bound must be integer',logger=gra_logger)

        if SC.sym == RCURLY:    SC.getSym()
        else:                   SC.mark('expected closing curly brace')

    else:
        SC.mark('unknown atom')
        base = None

    return base

def typ():
    if SC.sym not in FIRST_TYPE:
        SC.mark('attempt to parse {0} as TYPE'.format(SC.sym))

    if SC.sym == INT:
        base = Int()
    elif SC.sym == FLOAT:
        base = Float()
    elif SC.sym == STR:
        base = Str()
    elif SC.sym == BOOL:
        base = Bool()
    elif SC.sym == FUNC:
        base = Ref('func')
    elif SC.sym == LABEL:
        base = Ref('label')

    SC.getSym()

    if SC.sym == CAST:
        SC.getSym()

        if SC.sym == ARRAY:
            base = Array(base)
        elif SC.sym == LIST:
            base = List(base)
        else:
            SC.mark('unknown collection type')

        SC.getSym()

    return base

def lineend():
    if SC.sym not in FIRST_LINEEND:
        SC.mark('attempt to parse {0} as LINEEND'.format(SC.sym))
        while SC.sym not in FIRST_STMT:
            SC.getSym()

    if SC.sym == LINEEND:
        SC.getSym()
        if SC.sym == NEWLINE:
            SC.getSym()

    elif SC.sym == NEWLINE:
        SC.getSym()

    else:
        SC.mark('unknown lineend')

def execute(scanner, log=True):
    # Parse the program held in scanner SC
    from time import time
    global SC, gra_logger

    SC = scanner
    gra_logger = getLogger('grammar_{0}'.format(SC.fname))

    start = time()
    prog()
    end = time()

    gra_logger.info('grammar parse complete')
    gra_logger.info('elapsed time {0}s'.format(end-start))
    gra_logger.info('encountered error {0}'.format(SC.error))
