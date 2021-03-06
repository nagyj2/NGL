# NGL Speed Transcompiler

import ngl_s_sc as SC
from ngl_s_sc import PLUS, MINUS, MULT, DIV, AND, OR, EQ, LT, GT, NOT, INPUT, COLON, LINEEND, LPAREN, RPAREN, LCURLY, COMMA, RCURLY, BOOL, NUMBER, RAW_STRING, INT, FLOAT, STRING, BOOLEAN, IDENT, IF, ASSIGN, BLOCK, ELSE, PRINT, LOOP, EXIT, EOF, mark, getSym
import ngl_s_ast as AST

# TODO: atoms beside each other in expressions are multipled/ appended

FIRSTATOM  = {IDENT, NUMBER, BOOL, RAW_STRING, LPAREN, INPUT}
FOLLOWATOM = {IDENT, NUMBER, BOOL, RAW_STRING, RPAREN, INPUT}

FIRSTSUBATOM  = {INT, FLOAT, STRING, BOOLEAN} | FIRSTATOM
FOLLOWSUBATOM =  FOLLOWATOM

FIRSTEXPR_L4  = {NOT} | FIRSTSUBATOM
FOLLOWEXPR_L4 = FOLLOWSUBATOM

FIRSTEXPR_L3  = FIRSTEXPR_L4
FOLLOWEXPR_L3 = FOLLOWEXPR_L4

FIRSTEXPR_L2  = {PLUS, MINUS} | FIRSTEXPR_L3
FOLLOWEXPR_L2 = FOLLOWEXPR_L3

FIRSTEXPR_L1  = FIRSTEXPR_L2
FOLLOWEXPR_L1 = FOLLOWEXPR_L2

FIRSTEXPR  = FIRSTEXPR_L1
FOLLOWEXPR = FOLLOWEXPR_L1

FIRSTSTMT  = {IDENT, IF, PRINT, LOOP, EXIT, LCURLY}
FOLLOWSTMT = {INPUT, RCURLY} | FOLLOWEXPR

FIRSTLINES  = FIRSTSTMT
FOLLOWLINES = {LINEEND}

FIRSTPROGRAM  = FIRSTLINES
FOLLOWPROGRAM = FOLLOWLINES

def program():
    if SC.sym not in FIRSTPROGRAM:
        mark('expected valid program start')

    prog = []

    while SC.sym in FIRSTPROGRAM:
        prog.append(lines())

    return prog

def lines():
    if SC.sym not in FIRSTLINES:
        mark('expected valid lines start')

    if SC.sym in FIRSTSTMT:
        val = stmt()

        if SC.sym == LINEEND:
            getSym()
        else:
            mark('expected semicolon')

        if SC.sym in FOLLOWLINES:
            mark('warning: empty line')
            while SC.sym in FOLLOWLINES:
                getSym()

    else:
        mark('unknown enum lines')

    return val

def stmt():
    if SC.sym not in FIRSTSTMT:
        mark('expected valid stmt start')

    if SC.sym == IDENT:
        # Set variable
        name = [AST.Node(IDENT,SC.val)]
        getSym()

        while SC.sym == COMMA:
            getSym()
            if SC.sym == IDENT:
                name.append(AST.Node(IDENT,SC.val))
                getSym()
            else:
                mark('expected identifier')

        if SC.sym in {EQ,PLUS,MINUS,MULT,DIV}:
            op = SC.sym
            getSym()
        else:
            op = EQ # Assume regular assignment
            # mark('expected assignment operator')

        value = [expr()]

        while SC.sym == COMMA:
            getSym()
            value.append(expr())

        if len(name) != len(value):
            mark('number of identifiers must equal number of expressions')

        if len(name) == len(value) == 1:
            val = AST.AssignNode(name[0],op,value[0])
        else:
            val = AST.SepNode(name,op,value)

    elif SC.sym == IF:
        # if statement
        getSym()
        cond = expr()
        true = stmt()

        # if SC.sym == LINEEND:
        #     getSym()
        # else:
        #     mark('expected semicolon after true branch')

        if SC.sym == ELSE:
            getSym()
            false = stmt()
        else:
            false = None

        val = AST.IfNode(cond,true,false)

    elif SC.sym == PRINT:
        # print stmt
        getSym()
        display = expr()
        val = AST.PrintNode(display)

    elif SC.sym == LOOP:
        # loop stmt
        getSym()
        cond = expr()
        if SC.sym == COLON:
            getSym()
        else:
            mark('expected colon')

        if SC.sym in FIRSTSTMT:
            first = stmt()
        else:
            first = None

        if SC.sym == COLON:
            getSym()
        else:
            mark('expected colon')

        if SC.sym in FIRSTSTMT:
            last = stmt()
        else:
            last = None

        if SC.sym == COLON:
            getSym()
        else:
            mark('expected colon')

        if SC.sym in FIRSTSTMT:
            body = stmt()
        else:
            body = None

        val = AST.LoopNode(cond,first,last,body)

    elif SC.sym == EXIT:
        # print stmt
        getSym()
        val = AST.ExitNode()

    elif SC.sym == LCURLY:
        # stmt block
        getSym()

        lst = []
        while SC.sym in FIRSTLINES:
            lst.append(lines())

        if SC.sym == RCURLY:
            getSym()
        else:
            mark('expected closing curly brace')

        val = AST.BlockNode(lst)

    else:
        mark('invalid enum stmt')

    return val

def expr():
    if SC.sym not in FIRSTEXPR:
        mark('expected valid expr start')

    val = expr_l1()

    while SC.sym in {AND, OR}:
        op = SC.sym
        getSym()
        mod = expr_l1()

        val = AST.BinOp(op,val,mod)

    return val

def expr_l1():
    if SC.sym not in FIRSTEXPR_L1:
        mark('expected valid expr_l1 start')

    val = expr_l2()

    while SC.sym in {EQ, LT, GT}:
        op = SC.sym
        getSym()
        mod = expr_l2()

        val = AST.BinOp(op,val,mod)

    return val

def expr_l2():
    if SC.sym not in FIRSTEXPR_L2:
        mark('expected valid expr_l2 start')

    unary = False
    if SC.sym == PLUS or SC.sym == MINUS:
        op = SC.sym
        getSym()

    val = expr_l3()

    if unary:
        val = UnOp(op,val)

    while SC.sym in {PLUS, MINUS}:
        op = SC.sym
        getSym()
        mod = expr_l3()

        val = AST.BinOp(op,val,mod)

    return val

def expr_l3():
    if SC.sym not in FIRSTEXPR_L3:
        mark('expected valid expr_l3 start')

    val = expr_l4()

    while SC.sym in {MULT, DIV}:
        op = SC.sym
        getSym()
        mod = expr_l4()

        val = AST.BinOp(op,val,mod)

    return val

def expr_l4():
    if SC.sym not in FIRSTEXPR_L3:
        mark('expected valid expr_l3 start')

    if SC.sym == NOT:
        getSym()
        val = AST.UnOp(NOT,subatom())
    else:
        val = subatom()

    return val

def subatom():
    if SC.sym not in FIRSTSUBATOM:
        mark('expected valid subatom start')

    if SC.sym == INT:
        getSym(); val = AST.UnOp(INT,atom())
    elif SC.sym == FLOAT:
        getSym(); val = AST.UnOp(FLOAT,atom())
    elif SC.sym == STRING:
        getSym(); val = AST.UnOp(STRING,atom())
    elif SC.sym == BOOLEAN:
        getSym(); val = AST.UnOp(BOOLEAN,atom())
    else:
        val = atom()

    if SC.sym in {INT, FLOAT, STRING, BOOLEAN}:
        mark('cast goes before expression')

    return val

def atom():
    if SC.sym not in FIRSTATOM:
        mark('expected valid atom start')

    if SC.sym == IDENT:
        # identifier
        value = AST.Node(IDENT,SC.val)
        getSym()

    elif SC.sym == NUMBER:
        # int or float
        if type(SC.val) == int:
            value = AST.Node(INT,SC.val)
        elif type(SC.val) == float:
            value = AST.Node(FLOAT,SC.val)
        getSym()

    elif SC.sym == BOOL:
        # true token
        value = AST.Node(BOOL,True)
        getSym()

    elif SC.sym == RAW_STRING:
        # string
        value = AST.Node(RAW_STRING,SC.val)
        getSym()

    elif SC.sym == INPUT:
        # string
        value = AST.Node(INPUT,None)
        getSym()

    elif SC.sym == LPAREN:
        # nested expression
        getSym()

        sub_val = expr()
        value = AST.Node(BLOCK,sub_val)

        if SC.sym == RPAREN:
            getSym()
        else:
            mark('expected closing bracket')

    else:
        mark('invalid enum atom')
        value = None

    return value

def _readsource(fname):
    src = ''
    with open(fname+'.ngls','r') as reader:
        for line in reader.readlines():
            src += line
    return src

def translate(fname):
    src = _readsource(fname)
    SC.init(fname, src)
    return program()


if __name__ == '__main__':
    fname = 'usr'
    lst = translate(fname)

    for line in lst:
        print(line)

'''
While (True)
     N = remainder from Total divided by 3
     If N > 0 Then
          Subtract N From Total
     Else
          Subtract 1 From Total
     Inform user of the results
     If Total is 0 Then print "I win" and exit
     Prompt user for input: Enter 1 or 2
     While (Input < 1 Or Input > 2)
           Print error message
           Re-prompt user for input
      If Total = 0 Then print "You win" and exit
'''
