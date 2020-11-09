# NGL Bytecode 2.0 Function Library

from math import log10
import bc2_1_sc as SC
from bc2_1_sc import PLUS, MINUS, MULT, DIV, MOD, EXP, AND, OR, NOT, E_NOT, EQ, NE, LT, GT, GOARROW1, GOARROW2, RETARROW1, RETARROW2, ARROW_SHAFT, NOJUMP, COMMA, COLON, CAST, SEMICOLON, PARAM, LPAREN, RPAREN, LBRAK, RBRAK, LCURLY, RCURLY, INT, FLOAT, BOOL, STRING, ARRAY, LIST, NULL, NUMBER, RAW_STRING, BOOLEAN, IDENT, VAR, SET, GOTO, IF, COMPARE, PRINT, READ, DELETE, TRY, RETURN, TYPE, LABEL, LEN, EOF, getSym, mark
import bc2_1_st as ST
from bc2_1_e import Variable, Collection

def func_label(param : list) -> Variable:
    if type(param) != list:
        raise Exception('param list expected')

    if len(param) == 1:
        arg1 = param[0]
        if not (arg1.typ == STRING): mark('label function requires 1 string argument')
        line = ST.getJmp(arg1.value)
        if type(line) != int:
            mark('unknown jump label')
            line = SC.line

        ret_val = Variable(INT,line)

    # elif len(param) == 2:
    #     arg1,arg2 = param[0],param[1]
    #     if not (arg1.typ == STRING and arg2.typ == INT):
    #         mark('2-argument label function requires 1 string and int argument')
    #         ret_val = SC.line
    #     elif arg1.value not in {'->', '<-', '=>', '<='}:
    #         mark('2-argument label funciton arg1 must be jump arrow')
    #         ret_val = SC.line
    #     else:
    #         line = ST.getSpc(arg1.value)[arg2.value]
    #
    #     if type(line) != int:
    #         mark('unknown arrow jump location')
    #         line = SC.line
    #
    #     ret_val = Variable(INT,line)

    else:
        mark('unkown usage of label function')
        ret_val = Variable(INT,-1)

    return ret_val

def func_len(param : list) -> Variable:
    if type(param) != list:
        raise Exception('param list expected')

    if len(param) == 1:
        arg = param[0]

        if arg.typ in {INT, FLOAT}:
            if arg.value > 0:    ret_val = int(log10(arg.value))+1
            elif arg.value == 0: ret_val = 1
            else:                ret_val = int(log10(-arg.value))+1 # +1 if you don't count the '-'
        elif arg.typ == STRING:  ret_val = len(arg.value)
        elif arg.typ == BOOL:    ret_val = 1

    else:
        mark('1 argument required for len function'); ret_val = -1

    return Variable(INT,ret_val)

def func_type(param : list) -> Variable:
    if type(param) != list:
        raise Exception('param list expected')

    if len(param) == 2:
        arg1,arg2 = param[0], param[1]
        ret_val = arg1.typ == arg2.typ

    else:
        mark('2 arguments required for type function'); ret_val = False

    return Variable(BOOL,ret_val)
