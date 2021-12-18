# NGL Bytecode 3.0 Interpreter
from copy import deepcopy
from bc3_scanner import Scanner, ENOT, CALL, BACK, CALLEND, PARAM, PERIOD, RANGE, TE, BACKQUOTE, OR, UNION, AND, INTER, EQ, NE, LT, GT, PLUS, MINUS, MULT, DIV, INTDIV, MOD, EXP, CAST, APPEND, BURROW, VAR, CONST, GLOBAL, READ, SET, DEL, GOTO, IF, TRY, EXEC, PRINT, INCLUDE, QUIT, RETURN, LOG, GOARROW1, GOARROW2, RETARROW1, RETARROW2, TILDE, LPAREN, RPAREN, LBRAK, RBRAK, LCURLY, RCURLY, COMMA, COLON, NONE, NUMBER, DECIMAL, STRING, IDENT, LINEEND, NEWLINE, EOF, ARROWS, FIRST_LABEL, LAST_LABEL, FIRST_LINEEND, LAST_LINEEND, FIRST_ATOM, LAST_ATOM, FIRST_INDEXED, LAST_INDEXED, FIRST_ELEMENT, LAST_ELEMENT, FIRST_UN_EXPR, LAST_UN_EXPR, FIRST_EXP_EXPR, LAST_EXP_EXPR, FIRST_MULT_EXPR, LAST_MULT_EXPR, FIRST_ADD_EXPR, LAST_ADD_EXPR, FIRST_CMP_EXPR, LAST_CMP_EXPR, FIRST_EQ_EXPR, LAST_EQ_EXPR, FIRST_DIS_EXPR, LAST_DIS_EXPR, FIRST_CJN_EXPR, LAST_CJN_EXPR, FIRST_ENT_EXPR, LAST_ENT_EXPR, FIRST_EXPR, LAST_EXPR, FIRST_STMT, LAST_STMT, FIRST_LINE, LAST_LINE, FIRST_PROG, LAST_PROG, STRONGSYMS, WEAKSYMS, FOLLOW_LINE, FOLLOW_IDENT, FOLLOW_STMT, FOLLOW_EXPR, FOLLOW_CJN_EXPR, FOLLOW_DIS_EXPR, FOLLOW_EQ_EXPR, FOLLOW_CMP_EXPR, FOLLOW_ADD_EXPR, FOLLOW_MULT_EXPR, FOLLOW_EXP_EXPR, FOLLOW_UN_EXPR, FOLLOW_ELEMENT, FOLLOW_INDEXED, FOLLOW_ATOM, FOLLOW_PROG, FIRST_INDEX, LAST_INDEX, FOLLOW_INDEX
import bc3_symboltable as ST
from bc3_processor import execute_function_grammar

from bc3_logging import getLogger
from bc3_data import Int, Float, Str, Bool, Func, Lab, Ref, Arr, Lst, Type

_logger = getLogger('dummy') # Dummy logger
islog = False # Is logging enabled
instate = {} # Intitial state

def prog():
    global SC
    if SC.sym not in FIRST_PROG:
        _logger.error('{0} attempt to parse {1} as PROG'.format(SC.lineInfo(),SC.sym))
        SC.setError()
        while SC.sym not in STRONGSYMS | FOLLOW_PROG:
            _logger.info('consumed {0}'.format(SC.sym)); SC.getSym()
        return

    while SC.sym in FIRST_LINE:
        line()

def line():
    global SC
    if SC.sym not in FIRST_LINE:
        _logger.error('{0} attempt to parse {1} as LINE'.format(SC.lineInfo(),SC.sym))
        SC.setError()
        while SC.sym not in STRONGSYMS | FOLLOW_LINE:
            _logger.info('consumed {0}'.format(SC.sym)); SC.getSym()
        return

    while SC.sym in ARROWS:
        ST.setSpc(SC.sym,SC.line)
        _logger.info('{0} added to arrow {1} jump with {2}'.format(SC.lineInfo(),SC.sym,SC.line))
        SC.getSym()

    if SC.sym == IDENT:
        jumplabel = Lab(SC.line,True) # const prevents changing a literal label's value, causing mass confusion
        ST.newSym(SC.val,jumplabel)
        _logger.info('{0} label {1} jump to {2}'.format(SC.lineInfo(),SC.val,SC.line))
        SC.getSym()
        if SC.sym == COLON: SC.getSym()
        else:               SC.mark('expected colon, got {0}'.format(SC.sym))

    if SC.sym in FIRST_STMT:
        stmt()

    lineend()

def label():
    global SC
    # TODO: check for arow desination existance
    if SC.sym not in FIRST_LABEL:
        _logger.error('{0} attempt to parse {1} as LABEL'.format(SC.lineInfo(),SC.sym))
        SC.setError()
        while SC.sym not in STRONGSYMS | FOLLOW_LABEL:
            _logger.info('consumed {0}'.format(SC.sym)); SC.getSym()
        return

    if SC.sym in ({TILDE,GOARROW1,GOARROW2}):
        back = 0
        while SC.sym == TILDE: SC.getSym(); back += 1

        if SC.sym not in set({GOARROW1,GOARROW2}):
            SC.mark('expected arrow, got {0}'.format(SC.sym))
        else:
            arrow = SC.sym
            SC.getSym()

            # line = ST.getNextArrow(arrow,SC.line,back) # cannot jump to future arrows b/c they arent parsed

    elif SC.sym in set({RETARROW1,RETARROW2}):
        arrow, back = SC.sym, 0
        SC.getSym()
        while SC.sym == TILDE: SC.getSym(); back += 1

        # line = ST.getNextArrow(arrow,SC.line,back)

    elif SC.sym == IDENT:
        SC.getSym()

    else:
        SC.mark('expected label, got {0}'.format(SC.sym))

def stmt():
    global SC, missing
    if SC.sym not in FIRST_STMT:
        _logger.error('{0} attempt to parse {1} as STMT'.format(SC.lineInfo(),SC.sym))
        SC.setError()
        while SC.sym not in STRONGSYMS | FOLLOW_STMT:
            _logger.info('consumed {0}'.format(SC.sym)); SC.getSym()
        return

    if SC.sym == GLOBAL:    glob = True; SC.getSym()
    else:                   glob = False

    if glob and SC.sym not in set({VAR,CONST,DEL,INCLUDE}):
        _logger.error('{0} only \'var\' and \'const\' can be global'.format(SC.lineInfo()))
        SC.setError()
        while SC.sym not in STRONGSYMS | FOLLOW_STMT:
            _logger.info('consumed {0}'.format(SC.sym)); SC.getSym()
        return

    if SC.sym in set({VAR,CONST}):
        # TODO: log var, type and val if present
        constant = True if SC.sym == CONST else False
        level = 0 if glob else -1
        SC.getSym()

        if SC.sym == IDENT:
            name = SC.val
        else:
            SC.mark('expected identifier, got {0}'.format(SC.sym))
            name = '_'

        # Create symbol for referencing
        ST.newSym(name,Ref('ident'),level)

        base = element() # get ident with optional cast, index
        if type(base) != Type: #== Ref and type(base.sub) == Ref.Ident:
            _logger.warning('{0} expected type, got {1}'.format(SC.lineInfo(),base))
        else: # Peel back type for checking
            base = base.sub

        # auto = True if type(base.sub) == Ref.Auto else False
        # else: # consume the Type wrapper
        #     base = base.sub

        if SC.sym in FIRST_EXPR or constant:
            exprType = expr()
            if type(exprType) == Type:
                isType = True
                exprType = exprType.sub # peel back type if present
            else:
                isType = False

            # TODO: improve
            if type(base.sub) in set({Lst,Ref}) or type(exprType) in set({Ref}) or base == exprType or base == exprType:
                # Known compatibility - Copy any metadata
                base = Type(exprType) if isType else exprType
            else:
                _logger.error('{0} incorrect expression type, expected {1} got {2}'.format(SC.lineInfo(),base,exprType))
                SC.setError()

        if type(base) == Ref and type(base.sub) == Ref.Ident:
            missing.add(name)

        base.const = constant
        # Assign 'real' type
        ST.setSym(name,base,level)

    elif SC.sym == READ:
        # TODO: complete
        SC.getSym()

        if SC.sym == IDENT:
            name = SC.val
        else:
            SC.mark('expected identifier, got {0}'.format(SC.sym))
            name = '_'

        base = element() # get ident with optional cast, index
        _logger.info('{0} variable {1} assigned input type {2}'.format(SC.lineInfo(),name, base))

        # If casted, known type. If ref, unknown
        if ST.hasSym(name):
            if  type(base) == Ref:  ST.setSym(name,Ref('input'))
            else:                   ST.setSym(name,base)
        else:
            if  type(base) == Ref:  ST.newSym(name,Ref('input'))
            else:                   ST.newSym(name,base)

    elif SC.sym == SET:
        SC.getSym()

        if SC.sym == IDENT:
            name = SC.val
        else:
            SC.mark('expected identifier, got {0}'.format(SC.sym))
            name = '_'

        # base = ST.getSym(name) # get type of identifier -> old method
        base = indexed() # get ident with optional cast, index

        if SC.sym in FIRST_EXPR:    exprType = expr()
        elif SC.sym == CAST:
            SC.mark('type not required for set','warning');
            if SC.sym == CAST:          SC.getSym()
            if SC.sym in FIRST_INDEXED: indexed()
            exprType = expr()
        else:
            SC.mark('expected expression, got {0}'.format(SC.sym))
            exprType = Ref('null')

        if base.const:
            _logger.error('{0} constants cannot be reassigned, got {1}'.format(SC.lineInfo(),name))
            SC.setError()
            return

        if base != exprType:
            _logger.error('{0} variable type mismatch, expected {1} got {2}'.format(SC.lineInfo(),base,exprType))
            SC.setError()
            return

        if type(exprType) == Ref and type(exprType.sub) == Ref.Ident:
            missing.add(name)

        exprType.const = False
        ST.setSym(name,exprType)

    elif SC.sym == DEL:
        SC.getSym()
        level = 0 if glob else -1

        if SC.sym == IDENT:

            while SC.sym == IDENT:
                name = SC.val # protected by while loop
                base = indexed() # base isnt used

                if ST.hasSym(name): ST.delSym(name,level)
                else: _logger.warning('{0} variable {1} does not exist'.format(SC.lineInfo(),name))

            if SC.sym not in FOLLOW_STMT:
                SC.mark('expected end of statement, got {0}'.format(SC.sym))
                while SC.sym not in FOLLOW_STMT:
                    _logger.info('consumed {0}'.format(SC.sym)); SC.getSym()

        else:
            SC.mark('expected identifier, got {0}'.format(SC.sym))

    elif SC.sym == GOTO:
        SC.getSym()

        if SC.sym in FIRST_LABEL:
            label()
        else:
            SC.mark('expected label, got {0}'.format(SC.sym))
            while SC.sym not in FOLLOW_STMT:
                _logger.info('consumed {0}'.format(SC.sym)); SC.getSym()

    elif SC.sym == IF:
        SC.getSym()

        if SC.sym in FIRST_EXPR:
            exprType = expr()
        else:
            SC.mark('expected expression, got {0}'.format(SC.sym))
            exprType = Ref('null')

        if type(exprType) not in set({Bool,Ref}):
            _logger.warning('{0} expected boolean, got {1}'.format(SC.lineInfo(),exprType))

        if SC.sym in FIRST_LABEL:
            label()
        else:
            SC.mark('expected label, got {0}'.format(SC.sym))
            while SC.sym not in FOLLOW_STMT:
                _logger.info('consumed {0}'.format(SC.sym)); SC.getSym()

    elif SC.sym == EXEC:
        SC.getSym()

        if SC.sym in FIRST_EXPR:    expr()
        else:                       SC.mark('expected expression, got {0}'.format(SC.sym))

    elif SC.sym == TRY:
        SC.getSym()

        if SC.sym in FIRST_STMT:
            stmt()
        else:
            SC.mark('expected statement, got {0}'.format(SC.sym))
            while SC.sym not in FOLLOW_STMT:
                _logger.info('consumed {0}'.format(SC.sym)); SC.getSym()
            return

        if SC.sym in FIRST_LABEL:
            label()
        else:
            SC.mark('expected label, got {0}'.format(SC.sym))
            while SC.sym not in FOLLOW_STMT:
                _logger.info('consumed {0}'.format(SC.sym)); SC.getSym()

    elif SC.sym == PRINT:
        SC.getSym()

        if SC.sym in FIRST_EXPR:
            exprType = expr()
        else:
            SC.mark('expected expression, got {0}'.format(SC.sym))
            exprType = Ref('null')

        if type(exprType) not in set({Str,Ref}):
            _logger.warning('{0} expected str type, got {1}'.format(SC.lineInfo(),exprType))

    elif SC.sym == INCLUDE:
        SC.getSym()
        level = 0 if glob else -1

        if SC.sym == IDENT:
            name = SC.val; SC.getSym()
            ST.newSym(name,Func('{0}.ngl'.format(name)),level)
            while SC.sym == IDENT:
                name = SC.val; SC.getSym()
                ST.newSym(name,Func('{0}.ngl'.format(name)),level)

            if SC.sym not in FOLLOW_STMT:
                SC.mark('expected end of statement, got {0}'.format(SC.sym))
                while SC.sym not in FOLLOW_STMT:
                    _logger.info('consumed {0}'.format(SC.sym)); SC.getSym()
        else:
            SC.mark('expected identifier, got {0}'.format(SC.sym))
            while SC.sym not in FOLLOW_STMT:
                _logger.info('consumed {0}'.format(SC.sym)); SC.getSym()

    elif SC.sym == QUIT:
        SC.getSym()
        _logger.info('{0} interpreter quit'.format(SC.lineInfo()))
        # quit()

    elif SC.sym == RETURN:
        SC.getSym()
        _logger.info('{0} interpreter return'.format(SC.lineInfo()))

        if SC.sym in FIRST_EXPR:
            exprType = expr()
        else:
            SC.mark('expected expression, got {0}'.format(SC.sym))
            exprType = Ref('null')

        # ST.setSym('reti',exprType)

    elif SC.sym == LOG:
        SC.getSym()

        if SC.sym in FIRST_EXPR:
            fileType = expr()
        else:
            SC.mark('expected expression, got {0}'.format(SC.sym))
            fileType = Ref('null')

        if SC.sym in FIRST_EXPR:
            exprType = expr()
        else:
            SC.mark('expected expression, got {0}'.format(SC.sym))
            exprType = Ref('null')

        if type(fileType) not in set({Str,Ref}):
            _logger.warning('{0} expected str type, got {1}'.format(SC.lineInfo(),fileType))
        if type(exprType) not in set({Str,Ref}):
            _logger.warning('{0} expected str type, got {1}'.format(SC.lineInfo(),exprType))

def expr():
    global SC
    if SC.sym not in FIRST_EXPR:
        _logger.error('{0} attempt to parse {1} as EXPR'.format(SC.lineInfo(),SC.sym))
        SC.setError()
        while SC.sym not in STRONGSYMS | FOLLOW_EXPR:
            _logger.info('consumed {0}'.format(SC.sym)); SC.getSym()
        return Ref('null')

    inv = False
    if SC.sym == ENOT:  SC.getSym(); inv = True

    base = cjn_expr()

    if inv:
        if type(base) not in set({Bool,Ref}):
            _logger.error('{0} incompatible expression negation type, got {1}'.format(SC.lineInfo(),base))
            SC.setError()
        base = Bool()

    return base

def cjn_expr():
    global SC
    if SC.sym not in FIRST_CJN_EXPR:
        _logger.error('{0} attempt to parse {1} as CJN_EXPR'.format(SC.lineInfo(),SC.sym))
        SC.setError()
        while SC.sym not in STRONGSYMS | FOLLOW_CJN_EXPR:
            _logger.info('consumed {0}'.format(SC.sym)); SC.getSym()
        return Ref('null')

    base = dis_expr()

    if SC.sym in set({OR, UNION}):
        if SC.sym == OR and type(base) not in set({Bool,Ref}):
            _logger.warning('{0} incompatible logical OR type, got {1}'.format(SC.lineInfo(),base))
        elif SC.sym == UNION and type(base) not in set({Arr,Lst,Ref}):
            _logger.warning('{0} incompatible union type, got {1}'.format(SC.lineInfo(),base))

        while SC.sym in set({OR, UNION}):
            if SC.sym == OR:
                SC.getSym()
                mod = dis_expr()

                if type(mod) not in set({Bool,Ref}):
                    _logger.warning('{0} incompatible logical OR arg type, got {1}'.format(SC.lineInfo(),mod))

                base = Bool()

            elif SC.sym == UNION:
                SC.getSym()
                mod = dis_expr()

                if type(mod) not in set({Arr,Lst,Ref}):
                    _logger.warning('{0} incompatible union arg type, got {1}'.format(SC.lineInfo(),mod))

                base = Lst()

    return base

def dis_expr():
    global SC
    if SC.sym not in FIRST_DIS_EXPR:
        _logger.error('{0} attempt to parse {1} as DIS_EXPR'.format(SC.lineInfo(),SC.sym))
        SC.setError()
        while SC.sym not in STRONGSYMS | FOLLOW_DIS_EXPR:
            _logger.info('consumed {0}'.format(SC.sym)); SC.getSym()
        return Ref('null')

    base = eq_expr()

    if SC.sym in set({AND, INTER}):
        if SC.sym == AND and type(base) not in set({Bool,Ref}):
            _logger.warning('{0} incompatible logical AND type, got {1}'.format(SC.lineInfo(),base))
        elif SC.sym == INTER and type(base) not in set({Arr,Lst,Ref}):
            _logger.warning('{0} incompatible intersection type, got {1}'.format(SC.lineInfo(),base))

        while SC.sym in set({AND, INTER}):
            if SC.sym == AND:
                SC.getSym()
                mod = eq_expr()

                if type(mod) not in set({Bool,Ref}):
                    _logger.warning('{0} incompatible logical AND arg type, got {1}'.format(SC.lineInfo(),mod))

                base = Bool()

            elif SC.sym == INTER:
                SC.getSym()
                mod = eq_expr()

                if type(mod) not in set({Arr,Lst,Ref}):
                    _logger.warning('{0} incompatible intersection arg type, got {1}'.format(SC.lineInfo(),mod))

                base = Lst()

    return base

def eq_expr():
    global SC
    if SC.sym not in FIRST_EQ_EXPR:
        _logger.error('{0} attempt to parse {1} as EQ_EXPR'.format(SC.lineInfo(),SC.sym))
        SC.setError()
        while SC.sym not in STRONGSYMS | FOLLOW_EQ_EXPR:
            _logger.info('consumed {0}'.format(SC.sym)); SC.getSym()
        return Ref('null')

    base = cmp_expr()

    if SC.sym in set({EQ,NE,TE}):
        while SC.sym in set({EQ,NE,TE}):
            SC.getSym()

            mod = cmp_expr()

        base = Bool()

    return base

def cmp_expr():
    global SC
    if SC.sym not in FIRST_CMP_EXPR:
        _logger.error('{0} attempt to parse {1} as CMP_EXPR'.format(SC.lineInfo(),SC.sym))
        SC.setError()
        while SC.sym not in STRONGSYMS | FOLLOW_CMP_EXPR:
            _logger.info('consumed {0}'.format(SC.sym)); SC.getSym()
        return Ref('null')

    base = add_expr()

    if SC.sym in set({LT,GT}):
        if type(base) not in set({Int,Float,Str,Ref}):
            _logger.warning('{0} incompatible comparison type, got {1}'.format(SC.lineInfo(),base))
        # if type(base) in set({Arr,Lst}):
        #     SC.mark('collection type cannot take relational operators',logger=gra_logger)
        # elif type(base) in set({Bool}):
        #     SC.mark('boolean cannot take relational operators',logger=gra_logger)

        while SC.sym in set({LT,GT}):
            SC.getSym()

            mod = add_expr()

            if type(mod) not in set({Int,Float,Str,Ref}):
                _logger.warning('{0} incompatible comparison arg type, got {1}'.format(SC.lineInfo(),mod))

        base = Bool()

    return base

def add_expr():
    global SC
    if SC.sym not in FIRST_ADD_EXPR:
        _logger.error('{0} attempt to parse {1} as ADD_EXPR'.format(SC.lineInfo(),SC.sym))
        SC.setError()
        while SC.sym not in STRONGSYMS | FOLLOW_ADD_EXPR:
            _logger.info('consumed {0}'.format(SC.sym)); SC.getSym()
        return Ref('null')

    base = mult_expr()

    if SC.sym in set({PLUS,MINUS}):
        if type(base) not in set({Int,Float,Str,Ref}):
            _logger.warning('{0} incompatible additive type, got {1}'.format(SC.lineInfo(),base))

        # TODO FIX implement type checking (Int and Floats can work together and only Str will work with Str)

        while SC.sym in set({PLUS,MINUS}):
            SC.getSym()

            mod = mult_expr()

            if type(base) != type(mod) and type(base) != Ref and type(mod) != Ref:
                #type(mod) not in set({Int,Float,Str,Ref}):
                _logger.warning('{0} incompatible additive arg type, expected {1} got {2}'.format(SC.lineInfo(),base,mod))

            # REMOVE goes against the philosophy of no type conversions
            # if type(base) == Int and type(mod) == Float:
            #     base = Float()

    return base

def mult_expr():
    global SC
    if SC.sym not in FIRST_MULT_EXPR:
        _logger.error('{0} attempt to parse {1} as MULT_EXPR'.format(SC.lineInfo(),SC.sym))
        SC.setError()
        while SC.sym not in STRONGSYMS | FOLLOW_MULT_EXPR:
            _logger.info('consumed {0}'.format(SC.sym)); SC.getSym()
        return Ref('null')

    base = exp_expr()

    if SC.sym in set({MULT,DIV,INTDIV,MOD}):
        if type(base) not in set({Int,Float,Ref}):
            _logger.warning('{0} incompatible multiplicitive type, got {1}'.format(SC.lineInfo(),base))

        while SC.sym in set({MULT,DIV,INTDIV,MOD}):
            SC.getSym()

            mod = exp_expr()

            if type(base) != type(mod) and type(base) != Ref and type(mod) != Ref:
            # if type(mod) not in set({Int,Float,Ref}):
                _logger.warning('{0} incompatible multiplicitive arg type, expected {1} got {2}'.format(SC.lineInfo(),base,mod))

            # REMOVE goes against the philosophy of no type conversions
            # if type(base) == Int and type(mod) == Float:
            #     base = Float()

    return base

def exp_expr():
    global SC
    if SC.sym not in FIRST_EXP_EXPR:
        _logger.error('{0} attempt to parse {1} as EXP_EXPR'.format(SC.lineInfo(),SC.sym))
        SC.setError()
        while SC.sym not in STRONGSYMS | FOLLOW_EXP_EXPR:
            _logger.info('consumed {0}'.format(SC.sym)); SC.getSym()
        return Ref('null')

    base = un_expr()

    if SC.sym == APPEND:
        SC.mark('{0} exponentiation uses \'**\', not \'^\''.format(SC.lineInfo(),base),'warning')
        SC.sym = EXP

    if SC.sym == EXP:
        if type(base) not in set({Int,Float,Ref}):
            _logger.warning('{0} incompatible exponentiation type, got {1}'.format(SC.lineInfo(),base))

        while SC.sym == EXP:
            SC.getSym()

            mod = un_expr()

            if type(mod) not in set({Int,Float,Ref}):
                _logger.warning('{0} incompatible exponentiation arg type, got {1}'.format(SC.lineInfo(),base))

            # REMOVE goes against the philosophy of no type conversions?
            # if type(mod) == Float:
            base = Float() # always returns a float

    return base

def un_expr():
    global SC
    if SC.sym not in FIRST_UN_EXPR:
        _logger.error('{0} attempt to parse {1} as UN_EXPR'.format(SC.lineInfo(),SC.sym))
        SC.setError()
        while SC.sym not in STRONGSYMS | FOLLOW_UN_EXPR:
            _logger.info('consumed {0}'.format(SC.sym)); SC.getSym()
        return Ref('null')

    op = None
    if SC.sym in set({PLUS,MINUS,TILDE}): op = SC.sym; SC.getSym()

    base = element()

    if op == PLUS and type(base) not in set({Int,Float,Ref}):
        _logger.warning('{0} incompatible unary addition type, got {1}'.format(SC.lineInfo(),base))
    elif op == MINUS and type(base) not in set({Int,Float,Ref}):
        _logger.warning('{0} incompatible unary subtraction type, got {1}'.format(SC.lineInfo(),base))
    elif op == TILDE and type(base) not in set({Bool,Ref}):
        _logger.warning('{0} incompatible logical NOT type, got {1}'.format(SC.lineInfo(),base))

    return base

def element():
    global SC
    if SC.sym not in FIRST_ELEMENT:
        _logger.error('{0} attempt to parse {1} as ELEMENT'.format(SC.lineInfo(),SC.sym))
        SC.setError()
        while SC.sym not in STRONGSYMS | FOLLOW_ELEMENT:
            _logger.info('consumed {0}'.format(SC.sym)); SC.getSym()
        return Ref('null')

    base = indexed()
    lastbase = base

    while SC.sym in set({CAST}):
        SC.getSym()
        cast = indexed()

        if type(cast) == Type:
            if type(lastbase) in set({Type,Arr}) or type(base.sub) == Ref.Ident:
                if type(lastbase) == Arr: # collection (array::array)
                    base = Type(Arr(lastbase.sub))
                elif type(lastbase) == Type: # type on type (int::array) or (int::str)
                    # NOTE: sematically, Arr is the only type allowed to do this
                    if type(cast.sub) == Arr: # collection types are special
                        base = Type(Arr(lastbase.sub))
                    else:
                        base = Type(cast.sub)
                else: # new var (ident::int)
                    base = Type(cast.sub)
            else: # simple cast (42::str) or (10f::int::str)
                if type(cast.sub) == Arr: # collection types are special
                    base = Arr(lastbase)
                else:
                    base = cast.sub

        else:
            _logger.error('{0} expected type literal, got {1}'.format(SC.lineInfo(),cast))
            SC.setError()

        lastbase = base

    return base

def indexed():
    global SC
    if SC.sym not in FIRST_INDEXED:
        _logger.error('{0} attempt to parse {1} as INDEXED'.format(SC.lineInfo(),SC.sym))
        SC.setError()
        while SC.sym not in STRONGSYMS | FOLLOW_INDEXED:
            _logger.info('consumed {0}'.format(SC.sym)); SC.getSym()
        return Ref('null')

    base = atom()

    while SC.sym in set({LBRAK}):
        # Int, Float can be indexed for digits, string for chars, Lists and Arrays for elements
        SC.getSym()

        if type(base) in set({Int,Float}):  base = Int()
        elif type(base) in set({Str}):      base = Str()
        elif type(base) in set({Arr}):      base = base.sub
        elif type(base) in set({Lst}):      base = Ref('list')
        elif type(base) in set({Ref}):      pass
        else:
            _logger.error('{0} invalid type for indexing, got {1}'.format(SC.lineInfo(),base))
            SC.setError()
            base = Ref('null')

        sub = index()

        if SC.sym == RBRAK:
            SC.getSym()
        else:
            SC.mark('expected closing bracket, got {0}'.format(SC.sym))
            while SC.sym not in STRONGSYMS | FOLLOW_INDEXED:
                _logger.info('consumed {0}'.format(SC.sym)); SC.getSym()

    return base

def atom():
    global SC, checked, _logger, missing, islog, state
    if SC.sym not in FIRST_ATOM:
        _logger.error('{0} attempt to parse {1} as ATOM'.format(SC.lineInfo(),SC.sym))
        SC.setError()
        while SC.sym not in STRONGSYMS | FOLLOW_ATOM:
            _logger.info('consumed {0}'.format(SC.sym)); SC.getSym()
        return Ref('null')

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

        if SC.sym == BURROW:    burrow = True; SC.getSym()
        else:                   burrow = False

        if ST.hasSym(name, burrow=burrow):
            base = ST.getSym(name,burrow=burrow).clone() # dont return actual b/c of aliasing
        else:
            # FIX non-existant variables dont throw error
            _logger.warning('{0} variable {1} does not exist'.format(SC.lineInfo(),name))
            base = Ref('null')

    elif SC.sym == CALL:
        SC.getSym()

        if SC.sym == IDENT:
            name = SC.val
        else:
            SC.mark('{0} expected identifier, got {1}'.format(SC.lineInfo(),SC.sym))

        base = indexed()
        if type(base) != Func:
            _logger.error('{0} expected call of function, got {1}'.format(SC.lineInfo(),base))
            SC.setError()

        while SC.sym == PARAM:
            SC.getSym()
            sub = expr()

        if SC.sym == CALLEND:
            SC.getSym()

        if base.data not in checked:
            checked.add(base.data)
            # b/c vars global, the reference is overwritten by call. need to save
            oldSC, old_logger = SC, _logger
            oldmissing = missing
            execute_function_grammar(base.data,state,islog)
            SC, _logger = oldSC, old_logger
            missing = oldmissing
            ST.updateLink(SC)

        base = Ref('func')

    elif SC.sym == LPAREN:
        SC.getSym()
        base = expr()
        if SC.sym == RPAREN:
            SC.getSym()
        else:
            SC.mark('expected closing parenthesis, got {0}'.format(SC.sym))
            while SC.sym not in STRONGSYMS | FOLLOW_ATOM:
                _logger.info('consumed {0}'.format(SC.sym)); SC.getSym()

    elif SC.sym == BACKQUOTE:
        SC.getSym()

        base = expr()
        if SC.sym == BACKQUOTE:
            SC.getSym()
        else:
            SC.mark('expected backquote, got {0}'.format(SC.sym))
            while SC.sym not in STRONGSYMS | FOLLOW_ATOM:
                _logger.info('consumed {0}'.format(SC.sym)); SC.getSym()
        base = Str()

    elif SC.sym == LCURLY:
        SC.getSym()

        if SC.sym in FIRST_EXPR:
            base = expr()

            if SC.sym == COLON:
                SC.getSym()
                base = Arr(base.sub)

                if SC.sym in FIRST_EXPR:    sub = expr()
                else:                       sub = None

            else:
                sub = base
                base = Lst()

            if sub != None:

                if type(base) == Arr:
                    # extract the raw type
                    if type(sub) == Type: sub = sub.sub

                    if type(base) not in set({Ref}) and base.sub != sub:
                        _logger.error('{0} collection-element type mismatch, expected {1} got {2}'.format(SC.lineInfo(),base.sub,sub))
                        SC.setError()

                if SC.sym == COMMA:
                    if type(base) in set({Arr,Ref}) and base.sub != sub:
                        _logger.error('{0} collection-element type mismatch, expected {1} got {2}'.format(SC.lineInfo(),base.sub,sub))
                        SC.setError()

                    while SC.sym == COMMA:
                        SC.getSym()
                        sub = expr()

                        if type(base) in set({Arr,Ref}) and base.sub != sub:
                            _logger.error('{0} collection-element type mismatch, expected {1} got {2}'.format(SC.lineInfo(),base.sub,sub))
                            SC.setError()

                elif SC.sym == COLON:
                    SC.getSym()

                    if type(sub) not in set({Int,Ref}):
                        _logger.error('{0} lower bound must be integer, got {1}'.format(SC.lineInfo(),sub))
                        SC.setError()

                    top = expr()

                    if type(top) not in set({Int,Ref}):
                        _logger.error('{0} upper bound must be integer, got {1}'.format(SC.lineInfo(),top))

        else:
            base = Lst()

        if SC.sym == RCURLY:
            SC.getSym()
        else:
            SC.mark('expected closing curly brace, got {0}'.format(SC.sym))
            while SC.sym not in STRONGSYMS | FOLLOW_ATOM:
                _logger.info('consumed {0}'.format(SC.sym)); SC.getSym()

    else:
        SC.mark('unknown atom, got {0}'.format(SC.sym))
        base = None

    return base

def index():
    global SC
    if SC.sym not in FIRST_INDEX:
        _logger.error('{0} attempt to parse {1} as INDEX'.format(SC.lineInfo(),SC.sym))
        SC.setError()
        while SC.sym not in STRONGSYMS | FOLLOW_INDEX:
            _logger.info('consumed {0}'.format(SC.sym)); SC.getSym()
        return Ref('null')

    add = False
    if SC.sym == APPEND: add = True; SC.getSym()

    if SC.sym == BACK:
        SC.getSym()
        base = Int()

    elif SC.sym in FIRST_EXPR:
        base = expr()
        if type(base) not in set({Int,Ref}):
            _logger.error('{0} non-integer index, got {1}'.format(SC.lineInfo(),base))
            base = Ref('null')

        if SC.sym == COLON:
            SC.getSym()

            if add: _logger.warning('{0} cannot append over slice'.format(SC.lineInfo(),base))

            if SC.sym == BACK:
                SC.getSym()
            else: # if SC.sym in FIRST_EXPR:
                top = expr()
                if type(top) not in set({Int,Ref}):
                    _logger.error('{0} non-integer upper index, got {1}'.format(SC.lineInfo(),top))

    return base

def lineend():
    global SC
    if SC.sym not in FIRST_LINEEND:
        _logger.error('{0} attempt to parse {1} as LINEEND'.format(SC.lineInfo(),SC.sym))
        SC.setError()
        while SC.sym not in STRONGSYMS | FIRST_STMT:
            _logger.info('consumed {0}'.format(SC.sym)); SC.getSym()

    if SC.sym == LINEEND:
        SC.getSym()
        if SC.sym == NEWLINE:
            SC.getSym()

    elif SC.sym == NEWLINE:
        SC.getSym()

    else:
        SC.mark('unknown lineend, got {0}'.format(SC.sym))

def execute(scanner, instate={}, log=True):
    # Parse the program held in scanner SC
    from time import time
    global SC, _logger, islog, state

    SC, islog, state = scanner, log, instate
    if log:     _logger = getLogger('grammar_{0}'.format(SC.fname))

    # Add default variables
    ST.newSym('__file',Str())   # file name
    ST.newSym('__main',Bool())  # is a function call (false for main, true for func call)

    ST.newSym('argv',Lst())         # Argument list
    ST.newSym('retv',Lst())         # Return list
    ST.newSym('reti',Ref('spc'))    # Return element

    start = time()
    prog()
    end = time()
#
    _logger.info('grammar parse complete')
    _logger.info('elapsed time {0}s'.format(end-start))
    _logger.info('encountered error {0}'.format(SC.error))

    # TODO: Better way to communicate state of program with preprocessor
    #   maybe json?
    # return deepcopy(PP.savedStates)
