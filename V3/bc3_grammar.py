# NGL Bytecode 3.0 Grammar Skeleton

from bc3_scanner import Scanner
from bc3_scanner import ENOT, CALL, BACK, CALLEND, PARAM, TE, BACKQUOTE, OR, UNION, AND, INTER, EQ, NE, LT, GT, PLUS, MINUS, MULT, DIV, INTDIV, MOD, EXP, NOT, CAST, VAR, CONST, READ, SET, DEL, GOTO, IF, TRY, EXEC, PRINT, INCLUDE, QUIT, RETURN, LOG, GOARROW1, GOARROW2, RETARROW1, RETARROW2, ARROWSHAFT, LPAREN, RPAREN, LBRAK, RBRAK, LCURLY, RCURLY, COMMA, COLON, INT, FLOAT, STR, BOOL, ARRAY, LIST, FUNC, LABEL, NONE, NUMBER, DECIMAL, STRING, IDENT, LINEEND, NEWLINE, EOF, ARROWS, TYPES
from bc3_scanner import FIRST_LABEL, LAST_LABEL, FIRST_TYPE, LAST_TYPE, FIRST_CAST, LAST_CAST, FIRST_LINEEND, LAST_LINEEND, FIRST_ATOM, LAST_ATOM, FIRST_INDEXED, LAST_INDEXED, FIRST_ELEMENT, LAST_ELEMENT, FIRST_UN_EXPR, LAST_UN_EXPR, FIRST_EXP_EXPR, LAST_EXP_EXPR, FIRST_MULT_EXPR, LAST_MULT_EXPR, FIRST_ADD_EXPR, LAST_ADD_EXPR, FIRST_CMP_EXPR, LAST_CMP_EXPR, FIRST_EQ_EXPR, LAST_EQ_EXPR, FIRST_DIS_EXPR, LAST_DIS_EXPR, FIRST_CJN_EXPR, LAST_CJN_EXPR, FIRST_ENT_EXPR, LAST_ENT_EXPR, FIRST_EXPR, LAST_EXPR, FIRST_STMT, LAST_STMT, FIRST_LINE, LAST_LINE, FIRST_PROG, LAST_PROG
import bc3_symboltable as ST

from bc3_logging import getLogger
from bc3_data import Int, Float, Str, Bool, Func, Lab, Ref, Arr, Lst

# TODO: update logging to inform of check results

missing = [] # track variables missing values (Have ref @ end)
_logger = getLogger('dummy')

def prog():
    global SC
    if SC.sym not in FIRST_PROG:
        _logger.error('attempt to parse {0} as PROG'.format(SC.sym))
        SC.mark()

    while SC.sym in FIRST_LINE:
        line()

def line():
    global SC
    if SC.sym not in FIRST_LINE:
        _logger.error('attempt to parse {0} as LINE'.format(SC.sym))
        SC.mark()

    while SC.sym in ARROWS:
        ST.setSpc(SC.sym,SC.line)
        _logger.info('added to arrow {0} jump with {1}'.format(SC.sym,SC.line))
        SC.getSym()

    if SC.sym == IDENT:
        jumplabel = Lab(SC.line,True) # const prevents changing a literal label's value, causing mass confusion
        ST.newSym(SC.val,jumplabel)
        _logger.info('label {0} jump to {1}'.format(SC.val,SC.line))
        SC.getSym()
        if SC.sym == COLON: SC.getSym()
        else:               SC.mark('expected colon, got {0}'.format(SC.sym))

    if SC.sym in FIRST_STMT:
        stmt()

    lineend()

def label():
    global SC
    if SC.sym not in FIRST_LABEL:
        _logger.error('attempt to parse {0} as LABEL'.format(SC.sym))
        SC.mark()

    if SC.sym in ({ARROWSHAFT,GOARROW1,GOARROW2}):
        while SC.sym == ARROWSHAFT: SC.getSym()

        if SC.sym in set({GOARROW1,GOARROW2}):
            SC.getSym()
        else:
            SC.mark('expected arrow, got {0}'.format(SC.sym))

    elif SC.sym in set({RETARROW1,RETARROW2}):
        SC.getSym()
        while SC.sym == ARROWSHAFT: SC.getSym()

    elif SC.sym == IDENT:
        SC.getSym()

    else:
        SC.mark('expected label, got {0}'.format(SC.sym))

def stmt():
    global SC, missing
    if SC.sym not in FIRST_STMT:
        _logger.error('attempt to parse {0} as STMT'.format(SC.sym))
        SC.mark()

    if SC.sym == VAR:
        # TODO: log var, type and val if present
        SC.getSym()

        if SC.sym == IDENT:         name = SC.val
        else:                       SC.mark('expected identifier, got {0}'.format(SC.sym))

        # TODO: separate atom into two pieces, one is acceptable here and expr and other for expr only
        base = element() # get ident with optional cast, index

        # if SC.sym == CAST:          SC.getSym()
        # elif SC.sym == COLON:       SC.mark('expected cast or space, not colon'); SC.getSym()

        # if SC.sym in FIRST_TYPE:    varType = typ();
        # else:                       SC.mark('expected type, got {0}'.format(SC.sym)); varType = Int()

        if SC.sym in FIRST_EXPR:
            exprType = expr()

            if type(base) == Lab == type(exprType):
                base = exprType

            if base != exprType:
                _logger.error('incorrect expression type, expected {0} got {1}'.format(base,exprType))
                SC.mark()

        if type(base) == Ref and base.sub == 'ident':
            missing.append(name)

        base.const = False
        ST.newSym(name,base)

    elif SC.sym == CONST:
        # TODO: log var, type and val if present
        SC.getSym()

        if SC.sym == IDENT:         name = SC.val
        else:                       SC.mark('expected identifier, got {0}'.format(SC.sym))

        # TODO: separate atom into two pieces, one is acceptable here and expr and other for expr only
        base = element() # get ident with optional cast, index

        if SC.sym in FIRST_EXPR:    exprType = expr()
        else:                       SC.mark('expected expression, got {0}'.format(SC.sym))

        if type(base) == Lab == type(exprType):
            base = exprType
        elif type(base) == Func == type(exprType):
            base = exprType

        if base != exprType:
            _logger.error('incorrect expression type, expected {0} got {1}'.format(constType,exprType))
            SC.mark()

        if type(base) == Ref and base.sub == 'ident':
            missing.append(name)

        base.const = True
        ST.newSym(name,base)

    elif SC.sym == READ:
        # TODO: complete
        SC.getSym()

        if SC.sym == IDENT: name = SC.val
        else:               SC.mark('expected identifier, got {0}'.format(SC.sym))

        # TODO: separate atom into two pieces, one is acceptable here and expr and other for expr only
        base = element() # get ident with optional cast, index
        _logger.info('variable {0} assigned input type {0}'.format(name, base))

        # If casted, known type. If ref, unknown
        if ST.hasSym(name):
            if  type(base) == Ref:  ST.setSym(name,Ref('input'))
            else:                   ST.setSym(name,base)
        else:
            if  type(base) == Ref:  ST.newSym(name,Ref('input'))
            else:                   ST.newSym(name,base)

    elif SC.sym == SET:
        SC.getSym()

        if SC.sym == IDENT:         name = SC.val
        else:                       SC.mark('expected identifier, got {0}'.format(SC.sym))

        # TODO: separate atom into two pieces, one is acceptable here and expr and other for expr only
        base = indexed() # get ident with optional cast, index

        if SC.sym in FIRST_EXPR:    exprType = expr()
        elif SC.sym in FIRST_TYPE:  SC.mark('type not needed for set','warning'); typ()
        else:                       SC.mark('expected expression, got {0}'.format(SC.sym))

        if not ST.hasSym(name):
            _logger.error('variable {0} does not exist'.format(name))
            SC.mark()

        else:
            base = ST.getSym(name) # get type of identifier

            if base.const:
                _logger.error('constants cannot be reassigned, got {0}'.format(name))
                SC.mark()

            else:
                if base != exprType:
                    _logger.error('variable type mismatch, needed {0} got {1}'.format(base,exprType))
                    SC.mark()

                if type(exprType) == Ref and exprType.sub == 'ident':
                    missing.append(name)

                exprType.const = False
                ST.setSym(name,exprType)

    elif SC.sym == DEL:
        SC.getSym()

        if SC.sym == IDENT:

            while SC.sym == IDENT:
                name = SC.val # protected by while loop
                SC.getSym()
                # base = indexed() # base isnt used

                if ST.hasSym(name): ST.delSym(name)
                else:               _logger.warning('variable {0} does not exist'.format(name))

        else:
            SC.mark('expected identifier, got {0}'.format(SC.sym))

        # if constType != exprType:
        #     SC.mark('type mismatch',logger=gra_logger)

    elif SC.sym == GOTO:
        SC.getSym()

        if SC.sym in FIRST_LABEL:   label()
        else:                       SC.mark('expected label')

    elif SC.sym == IF:
        SC.getSym()

        if SC.sym in FIRST_EXPR:    exprType = expr()
        else:                       SC.mark('expected expression, got {0}'.format(SC.sym))

        if type(exprType) != Bool:
            _logger.warning('expected boolean, got {0}'.format(exprType))

        if SC.sym in FIRST_LABEL:   label()
        else:                       SC.mark('expected label, got {0}'.format(SC.sym))

    elif SC.sym == EXEC:
        SC.getSym()

        if SC.sym in FIRST_EXPR:    expr()
        else:                       SC.mark('expected expression, got {0}'.format(SC.sym))

    elif SC.sym == TRY:
        SC.getSym()

        if SC.sym in FIRST_STMT:    stmt()
        else:                       SC.mark('expected statement, got {0}'.format(SC.sym))

        if SC.sym in FIRST_LABEL:   label()
        else:                       SC.mark('expected label, got {0}'.format(SC.sym))

    elif SC.sym == PRINT:
        SC.getSym()

        if SC.sym in FIRST_EXPR:    exprType = expr()
        else:                       SC.mark('expected expression, got {0}'.format(SC.sym))

        if type(exprType) != Str:
            _logger.warning('expected str type, got {0}'.format(exprType))

    elif SC.sym == INCLUDE:
        SC.getSym()

        if SC.sym == IDENT:
            name = SC.val; SC.getSym()
            ST.newSym(name,Func('{0}.ngl'.format(name)))
            while SC.sym == IDENT:
                name = SC.val; SC.getSym()
                ST.newSym(name,Func('{0}.ngl'.format(name)))

        else:
            SC.mark('expected identifier, got {0}'.format(SC.sym))

    elif SC.sym == QUIT:
        SC.getSym()
        _logger.info('interpreter quit')
        # quit()

    elif SC.sym == RETURN:
        _logger.info('interpreter return')
        SC.getSym()

    elif SC.sym == LOG:
        SC.getSym()

        if SC.sym == FIRST_EXPR:    exprType = expr()
        else:                       SC.mark('expected expression, got {0}'.format(SC.sym))

        if type(exprType) != Str:
            _logger.warning('expected str type, got {0}'.format(exprType))

def expr():
    if SC.sym not in FIRST_EXPR:
        _logger.error('attempt to parse {0} as EXPR'.format(SC.sym))
        SC.mark()

    inv = False
    if SC.sym == ENOT:  SC.getSym(); inv = True

    base = cjn_expr()

    if inv:
        if type(base) != Bool:
            _logger.error('incompatible expression negation type, got {0}'.format(base))
            SC.mark()
        base = Bool()

    return base

def cjn_expr():
    if SC.sym not in FIRST_CJN_EXPR:
        _logger.error('attempt to parse {0} as CJN_EXPR'.format(SC.sym))
        SC.mark()

    base = dis_expr()

    if SC.sym in set({OR, UNION}):
        if SC.sym == OR and type(base) not in set({Bool}):
            _logger.warning('incompatible logical OR type, got {0}'.format(base))
        elif SC.sym == UNION and type(base) not in set({Arr,Lst}):
            _logger.warning('incompatible union type, got {0}'.format(base))

        while SC.sym in set({OR, UNION}):
            if SC.sym == OR:
                SC.getSym()
                mod = dis_expr()

                if type(mod) not in set({Bool}):
                    _logger.warning('incompatible logical OR arg type, got {0}'.format(mod))

                base = Bool()

            elif SC.sym == UNION:
                SC.getSym()
                mod = dis_expr()

                if type(mod) not in set({Arr,Lst}):
                    _logger.warning('incompatible union arg type, got {0}'.format(mod))

                base = Lst()

    return base

def dis_expr():
    if SC.sym not in FIRST_DIS_EXPR:
        _logger.error('attempt to parse {0} as DIS_EXPR'.format(SC.sym))
        SC.mark()

    base = eq_expr()

    if SC.sym in set({AND, INTER}):
        if SC.sym == AND and type(base) not in set({Bool}):
            _logger.warning('incompatible logical AND type, got {0}'.format(base))
        elif SC.sym == INTER and type(base) not in set({Arr,Lst}):
            _logger.warning('incompatible intersection type, got {0}'.format(base))

        while SC.sym in set({AND, INTER}):
            if SC.sym == AND:
                SC.getSym()
                mod = eq_expr()

                if type(mod) not in set({Bool}):
                    _logger.warning('incompatible logical AND arg type, got {0}'.format(mod))

                base = Bool()

            elif SC.sym == INTER:
                SC.getSym()
                mod = eq_expr()

                if type(mod) not in set({Arr,Lst}):
                    _logger.warning('incompatible intersection arg type, got {0}'.format(mod))

                base = Lst()

    return base

def eq_expr():
    if SC.sym not in FIRST_EQ_EXPR:
        _logger.error('attempt to parse {0} as EQ_EXPR'.format(SC.sym))
        SC.mark()

    base = cmp_expr()

    if SC.sym in set({EQ,NE,TE}):
        while SC.sym in set({EQ,NE,TE}):
            SC.getSym()

            mod = cmp_expr()

        base = Bool()

    return base

def cmp_expr():
    if SC.sym not in FIRST_CMP_EXPR:
        _logger.error('attempt to parse {0} as CMP_EXPR'.format(SC.sym))
        SC.mark()

    base = add_expr()

    if SC.sym in set({LT,GT}):
        if type(base) not in set({Int,Float,Str}):
            _logger.warning('incompatible comparison type, got {0}'.format(base))
        # if type(base) in set({Arr,Lst}):
        #     SC.mark('collection type cannot take relational operators',logger=gra_logger)
        # elif type(base) in set({Bool}):
        #     SC.mark('boolean cannot take relational operators',logger=gra_logger)

        while SC.sym in set({LT,GT}):
            SC.getSym()

            mod = add_expr()

            if type(mod) in set({Bool,Arr,Lst}):
                _logger.warning('incompatible comparison arg type, got {0}'.format(mod))

        base = Bool()

    return base

def add_expr():
    if SC.sym not in FIRST_ADD_EXPR:
        _logger.error('attempt to parse {0} as ADD_EXPR'.format(SC.sym))
        SC.mark()

    base = mult_expr()

    if SC.sym in set({PLUS,MINUS}):
        if type(base) not in set({Int,Float,Str}):
            _logger.warning('incompatible additive type, got {0}'.format(base))

        # TODO FIX implement type checking (Int and Floats can work together and only Str will work with Str)

        while SC.sym in set({PLUS,MINUS}):
            SC.getSym()

            mod = mult_expr()

            if type(mod) not in set({Int,Float,Str}):
                _logger.warning('incompatible additive arg type, got {0}'.format(mod))

            if type(base) == Int and type(mod) == Float:
                base = Float()

    return base

def mult_expr():
    if SC.sym not in FIRST_MULT_EXPR:
        _logger.error('attempt to parse {0} as MULT_EXPR'.format(SC.sym))
        SC.mark()

    base = exp_expr()

    if SC.sym in set({MULT,DIV,INTDIV,MOD}):
        if type(base) not in set({Int,Float,Str}):
            _logger.warning('incompatible multiplicitive type, got {0}'.format(base))

        while SC.sym in set({MULT,DIV,INTDIV,MOD}):
            SC.getSym()

            mod = exp_expr()

            if type(mod) not in set({Int,Float,Str}):
                _logger.warning('incompatible multiplicitive arg type, got {0}'.format(mod))

            if type(base) == Int and type(mod) == Float:
                base = Float()

    return base

def exp_expr():
    if SC.sym not in FIRST_EXP_EXPR:
    #     _logger.error('attempt to parse {0} as EXP_EXPR'.format(SC.sym))
        SC.mark()

    base = un_expr()

    if SC.sym == EXP:
        if type(base) not in set({Int,Float}):
            _logger.warning('incompatible exponentiation type, got {0}'.format(base))

        while SC.sym == EXP:
            SC.getSym()

            mod = un_expr()

            if type(base) not in set({Int,Float}):
                _logger.warning('incompatible exponentiation arg type, got {0}'.format(base))

            if type(mod) == Float:
                base = Float()

    return base

def un_expr():
    if SC.sym not in FIRST_UN_EXPR:
        _logger.error('attempt to parse {0} as UN_EXPR'.format(SC.sym))
        SC.mark()

    op = None
    if SC.sym == PLUS:      op = SC.sym; SC.getSym()
    elif SC.sym == MINUS:   op = SC.sym; SC.getSym()
    elif SC.sym == NOT:     op = SC.sym; SC.getSym()

    base = element()

    if op == PLUS and type(base) not in set({Int,Float}):
        _logger.warning('incompatible unary addition type, got {0}'.format(base))
    elif op == MINUS and type(base) not in set({Int,Float}):
        _logger.warning('incompatible unary subtraction type, got {0}'.format(base))
    elif op == PLUS and type(base) not in set({Bool}):
        _logger.warning('incompatible logical NOT type, got {0}'.format(base))

    return base

def element():
    if SC.sym not in FIRST_ELEMENT:
        _logger.error('attempt to parse {0} as ELEMENT'.format(SC.sym))
        SC.mark()

    base = indexed()

    if SC.sym in set({CAST}):

        SC.getSym()
        if SC.sym in FIRST_TYPE:    base = typ()
        else:                       SC.mark('expected type, got {0}'.format(SC.sym))

    return base

def indexed():
    if SC.sym not in FIRST_INDEXED:
        _logger.error('attempt to parse {0} as INDEXED'.format(SC.sym))
        SC.mark()

    base = atom()

    if SC.sym in set({LBRAK,BACK}):
        # Int, Float can be indexed for digits, string for chars, Lists and Arrays for elements
        if type(base) not in set({Int,Float,Str,Arr,Lst}):
            _logger.error('invalid type for indexing, got {0}'.format(base))
            SC.mark()

        if SC.sym == BACK: # match end of collection
            SC.getSym()

        elif SC.sym in FIRST_EXPR:
            sub = expr()

            if type(sub) not in set({Int}):
                _logger.error('invalid index type, got {0}'.format(sub))
                SC.mark()

            if SC.sym == RANGE:
                SC.getSym()

                if SC.sym == BACK:
                    SC.getSym()
                else:
                    mod = expr()
                    if type(mod) not in set({Int}):
                        _logger.error('invalid index type, got {0}'.format(mod))
                        SC.mark()

        else:
            _logger.error('invalid index, got {0}'.format(mod))
            SC.mark()

        if type(base) in set({Int,Float}):  base = Int()
        elif type(base) in set({Str}):      base = Str()
        elif type(base) in set({Arr}):      base = base.sub
        elif type(base) in set({Lst}):      base = Ref('list')

        if SC.sym == RBRAK: SC.getSym()
        else:               SC.mark('expected closing bracket, got {0}'.format(SC.sym))

    return base

def atom():
    if SC.sym not in FIRST_ATOM:
        _logger.error('attempt to parse {0} as ATOM'.format(SC.sym))
        SC.mark()

    if SC.sym == NUMBER:
        SC.getSym()
        base = Int()

    elif SC.sym == DECIMAL:
        SC.getSym()
        base = Float()

    elif SC.sym == STRING:
        SC.getSym()
        base = Str()

    elif SC.sym == IDENT:
        name = SC.val
        SC.getSym()
        if ST.hasSym(name): base = ST.getSym(name).clone() # dont return actual b/c of aliasing
        else:               base = Ref('ident')

    elif SC.sym == CALL:
        SC.getSym()

        name = expr()
        print(name)

        if type(name) != Func:
            _logger.error('attempt call non-function, got {0}'.format(name))
            SC.mark()

        while SC.sym == PARAM:
            SC.getSym()
            sub = expr()

        if SC.sym == CALLEND:
            SC.getSym()

    elif SC.sym == LPAREN:
        SC.getSym()

        base = expr()
        if SC.sym == RPAREN:    SC.getSym()
        else:                   SC.mark('expected closing parenthesis, got {0}'.format(SC.sym))

    elif SC.sym == BACKQUOTE:
        SC.getSym()

        base = expr()
        if SC.sym == BACKQUOTE: SC.getSym()
        else:                   SC.mark('expected backquote, got {0}'.format(SC.sym))
        base = Str()

    elif SC.sym == LCURLY:
        SC.getSym()

        base = typ()

        # ::array is optional
        if type(base) != Arr:
            base = Arr(base)

        if type(base) not in set({Arr}):
            _logger.error('invalid collection type, got {0}'.format(base))

        if SC.sym == COLON:     SC.getSym()
        elif SC.sym == CAST:    SC.mark('expected colon, not cast'.format(SC.sym))
        else:                   SC.mark('expected colon, got {0}'.format(SC.sym))

        if SC.sym in FIRST_EXPR:
            sub = expr() # subtype

            if SC.sym == COMMA:

                if base.sub != sub:
                    _logger.error('collection-element type mismatch, expected {0} got {1}'.format(base,sub))

                while SC.sym == COMMA:
                    SC.getSym()
                    sub = expr()

                    if base.sub != sub:
                        _logger.error('collection-element type mismatch, expected {0} got {1}'.format(base,sub))

            elif SC.sym == COLON:
                SC.getSym()

                if type(sub) != Int:
                    _logger.error('lower bound must be integer, got {0}'.format(sub))

                top = expr()

                if type(top) != Int:
                    _logger.error('upper bound must be integer, got {0}'.format(top))

        if SC.sym == RCURLY:    SC.getSym()
        else:                   SC.mark('expected closing curly brace, got {0}'.format(SC.sym))

    elif SC.sym == LBRAK:
        SC.getSym()

        base = Lst()

        if SC.sym in FIRST_EXPR:
            sub = expr() # subtype

            while SC.sym == COMMA:
                SC.getSym()
                sub = expr()

        if SC.sym == RBRAK: SC.getSym()
        else:               SC.mark('expected closing bracket, got {0}'.format(SC.sym))

    else:
        SC.mark('unknown atom, got {0}'.format(SC.sym))
        base = None

    return base

def typ():
    if SC.sym not in FIRST_TYPE:
        _logger.error('attempt to parse {0} as TYPE'.format(SC.sym))
        SC.mark()

    if SC.sym == INT:
        base = Int()
    elif SC.sym == FLOAT:
        base = Float()
    elif SC.sym == STR:
        base = Str()
    elif SC.sym == BOOL:
        base = Bool()
    elif SC.sym == FUNC:
        base = Func() # Ref('func')
    elif SC.sym == LABEL:
        base = Lab() # Ref('label')
    elif SC.sym == LIST:
        base = Lst()
    else:
        SC.mark('unknown primitive type, got {0}'.format(SC.sym))

    SC.getSym()

    if SC.sym in set({CAST}):
        SC.getSym()

        if SC.sym == ARRAY: base = Arr(base)
        else:               SC.mark('unknown collection type, got {0}'.format(SC.sym))

        SC.getSym()

    return base

def lineend():
    if SC.sym not in FIRST_LINEEND:
        _logger.error('attempt to parse {0} as LINEEND'.format(SC.sym))
        SC.mark()
        while SC.sym not in FIRST_STMT:
            SC.getSym()

    if SC.sym == LINEEND:
        SC.getSym()
        if SC.sym == NEWLINE:
            SC.getSym()

    elif SC.sym == NEWLINE:
        SC.getSym()

    else:
        SC.mark('unknown lineend, got {0}'.format(SC.sym))

def execute(scanner, log=True):
    # Parse the program held in scanner SC
    from time import time
    global SC, _logger

    SC = scanner
    if log:     _logger = getLogger('grammar_{0}'.format(SC.fname))

    # Add default variables
    ST.newSym('__file',Str())   # file name
    ST.newSym('__main',Bool())  # is a function call (false for main, true for func call)

    ST.newSym('true',Bool(True))    # add boolean constants
    ST.newSym('false',Bool(True))
    ST.newSym('argv',Lst())         # Argument list
    ST.newSym('retv',Lst())         # Return list
    ST.newSym('reti',Ref('spc'))    # Return element

    start = time()
    prog()
    end = time()

    _logger.info('grammar parse complete')
    _logger.info('elapsed time {0}s'.format(end-start))
    _logger.info('encountered error {0}'.format(SC.error))
