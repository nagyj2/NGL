# NGL Speed Abstract Syntax Tree
# Holds nodes which can be used to construct the program

from enum import Enum
from ngl_s_sc import FUNC_DEF, FUNC_CALL, FUNC_END, PARAM, PLUS, MINUS, MULT, DIV, MOD, AND, OR, EQ, LT, GT, NOT, INPUT, COLON, LINEEND, LPAREN, RPAREN, LCURLY, RCURLY, BOOL, NUMBER, RAW_STRING, IDENT, IF, ELSE, PRINT, LOOP, EXIT, BLOCK, ASSIGN, INT, FLOAT, STRING, BOOLEAN, EOF, mark

INT, FLOAT, STRING, BOOL, IDENT
binop = { PLUS: [[INT, FLOAT, None ,None, INT],
                 [FLOAT, FLOAT, None ,None, FLOAT],
                 [None, None, STRING ,None, STRING],
                 [None, None, None, None, None],
                 [INT, FLOAT, STRING, None, IDENT]],

          MINUS: [[INT, FLOAT, None ,None, INT],
                 [FLOAT, FLOAT, None ,None, FLOAT],
                 [None, None, None, None, None],
                 [None, None, None ,None, None],
                 [INT, FLOAT, None, None, IDENT]],

          MULT: [[INT, FLOAT, STRING ,None, INT],
                 [FLOAT, FLOAT, None ,None, FLOAT],
                 [STRING, None, STRING ,None, IDENT],
                 [None, None, None, None, None],
                 [INT, FLOAT, IDENT, None, IDENT]],

          MOD: [[INT, None, None ,None, INT],
                 [None, None, None ,None, None],
                 [None, None, None ,None, IDENT],
                 [None, None, None, None, None],
                 [INT, None, IDENT, None, IDENT]],

          DIV: [[FLOAT, FLOAT, None ,None, FLOAT],
                 [FLOAT, FLOAT, None ,None, FLOAT],
                 [None, None, None, None, None],
                 [None, None, None ,None, None],
                 [FLOAT, FLOAT, None, None, IDENT]],

          AND: [[None, None, None ,None, None],
                 [None, None, None ,None, None],
                 [None, None, None ,None, None],
                 [None, None, None, BOOL, IDENT],
                 [None, None, None, IDENT, IDENT]],

          OR: [[None, None, None ,None, None],
                 [None, None, None ,None, None],
                 [None, None, None ,None, None],
                 [None, None, None, BOOL, IDENT],
                 [None, None, None, IDENT, IDENT]],

          EQ: [[BOOL, BOOL, BOOL ,BOOL, BOOL],
                 [BOOL, BOOL, BOOL ,BOOL, BOOL],
                 [BOOL, BOOL, BOOL ,BOOL, BOOL],
                 [BOOL, BOOL, BOOL, BOOL, BOOL],
                 [BOOL, BOOL, BOOL, BOOL, BOOL]],

          LT: [[BOOL, BOOL, BOOL ,None, IDENT],
                 [BOOL, BOOL, None ,None, IDENT],
                 [BOOL, None, BOOL ,None, IDENT],
                 [None, None, None, None, None],
                 [IDENT, IDENT, IDENT, None, IDENT]],

          GT: [[BOOL, BOOL, BOOL ,None, IDENT],
                 [BOOL, BOOL, None ,None, IDENT],
                 [BOOL, None, BOOL ,None, IDENT],
                 [None, None, None, None, None],
                 [IDENT, IDENT, IDENT, None, IDENT]]
}

class Node:
    def __init__(self,typ,val):
        self.typ, self.val, self.indent = typ, val, 0

    def __str__(self):
        toRet = '' + self.indent * '| '
        if self.typ in {IDENT, INT, FLOAT}:
            toRet += str(self.val)
        elif self.typ == BOOL:
            toRet += str(self.val).lower()
        elif self.typ == RAW_STRING:
            toRet += '\'' + str(self.val) + '\''
        elif self.typ == BLOCK:
            toRet += str(self.val)
        elif self.typ == INPUT:
            toRet += 'READ'
        else:
            mark('unknown assignment type')
            toRet += 'ERROR:'+str(self.typ)+':'+str(self.val)
        return toRet

    def ast_print(self):
        toRet = '' + self.indent * '| '
        if self.typ == INPUT:
            toRet += 'READ'
        elif self.typ in {IDENT, INT, FLOAT}:
            toRet += str(self.val)
        elif self.typ == BOOL:
            toRet += str(self.val).lower()
        elif self.typ == RAW_STRING:
            toRet += '\'' + str(self.val) + '\''
        elif self.typ == BLOCK:
            toRet += self.val.ast_print()
        else:
            mark('unknown assignment type')
            toRet += 'ERROR:'+str(self.typ)+':'+str(self.val)
        return toRet

    def eval(self):
        if self.typ == INT:
            return INT
        elif self.typ == FLOAT:
            return FLOAT
        elif self.typ == RAW_STRING:
            return STRING
        elif self.typ == BOOL:
            return BOOL

        elif self.typ == IDENT:
            return IDENT
        elif self.typ == BLOCK:
            return self.val.eval()
        elif self.typ == INPUT:
            return INPUT
        mark('unknown node type')

class BinOp:
    def __init__(self,op, arg1, arg2):
        self.op, self.arg1, self.arg2, self.indent = op, arg1, arg2, 0

    def __str__(self):
        toRet = '' + self.indent * '| '
        toRet += '(' + str(self.arg1)

        if self.op == PLUS:
            toRet += '+'
        elif self.op == MINUS:
            toRet += '-'
        elif self.op == MULT:
            toRet += '*'
        elif self.op == MOD:
            toRet += '%'
        elif self.op == DIV:
            toRet += '/'
        elif self.op == EQ:
            toRet += '='
        elif self.op == LT:
            toRet += '<'
        elif self.op == GT:
            toRet += '>'
        elif self.op == OR:
            toRet += '|'
        elif self.op == AND:
            toRet += '&'
        else:
            mark('unknown binary operation')

        toRet += str(self.arg2) + ')'
        return toRet

    def ast_print(self):
        toRet = '' + self.indent * '| '
        toRet += '(' + self.arg1.ast_print()

        if self.op == PLUS:
            toRet += '+'
        elif self.op == MINUS:
            toRet += '-'
        elif self.op == MULT:
            toRet += '*'
        elif self.op == MOD:
            toRet += '%'
        elif self.op == DIV:
            toRet += '/'
        elif self.op == EQ:
            toRet += '='
        elif self.op == LT:
            toRet += '<'
        elif self.op == GT:
            toRet += '>'
        elif self.op == OR:
            toRet += ' or '
        elif self.op == AND:
            toRet += ' and '
        else:
            mark('unknown binary operation')

        toRet += self.arg2.ast_print() + ')'
        return toRet

    def eval(self):
        etyp1, etyp2 = self.arg1.eval(), self.arg2.eval()
        if etyp1 == INT: ind1 = 0
        elif etyp1 == FLOAT: ind1 = 1
        elif etyp1 == STRING: ind1 = 2
        elif etyp1 == BOOL: ind1 = 3
        elif etyp1 == IDENT: ind1 = 4
        if etyp2 == INT: ind2 = 0
        elif etyp2 == FLOAT: ind2 = 1
        elif etyp2 == STRING: ind2 = 2
        elif etyp2 == BOOL: ind2 = 3
        elif etyp2 == IDENT: ind2 = 4
        return binop[self.op][ind1][ind2] # Lookup table

        # if self.arg1.eval() == IDENT or self.arg2.eval() == IDENT:
        #     return IDENT
        # elif self.arg1.eval() == INPUT or self.arg2.eval() == INPUT:
        #     return INPUT
        # if self.op == PLUS:
        #     if self.arg1.eval() in {INT,FLOAT} and self.arg2.eval() in {INT,FLOAT}:
        #         return FLOAT if self.arg1.eval() == FLOAT or self.arg2.eval() == FLOAT else INT
        #     if self.arg1.eval() in IDENT and self.arg2.eval() in {INT,FLOAT}:
        #         return FLOAT if self.arg1.eval() == FLOAT or self.arg2.eval() == FLOAT else INT
        #     elif self.arg1.eval() == STRING and self.arg2.eval() == STRING:
        #         return STRING
        #     mark('unknown additon operand type')
        # elif self.op == MINUS:
        #     return FLOAT if self.arg1.eval() == self.arg2.eval() == FLOAT else INT
        # elif self.op == MULT:
        #     return FLOAT if self.arg1.eval() == self.arg2.eval() == FLOAT else INT
        # elif self.op == DIV:
        #     return FLOAT if self.arg1.eval() == self.arg2.eval() == FLOAT else INT
        # elif self.op == EQ:
        #     return BOOL
        # elif self.op == LT:
        #     return BOOL
        # elif self.op == GT:
        #     return BOOL
        # elif self.op == OR:
        #     return BOOL
        # elif self.op == AND:
        #     return BOOL
        # mark('unknown operand type')

class UnOp:
    def __init__(self,op,arg1):
        self.op, self.arg1, self.indent = op, arg1, 0

    def __str__(self):
        toRet = '' + self.indent * '| '
        force_bool = False
        if self.op in {NOT, MINUS}:
            if self.op == NOT:
                # toRet += '!'
                force_bool = True
            elif self.op == MINUS:
                toRet += '-'
            else:
                mark('unknown unary operation 1')
            if force_bool:
                toRet += '!((' + str(self.arg1) + ')::bool)'
            else:
                toRet += str(self.arg1)
        elif self.op in {INT, FLOAT, STRING, BOOLEAN}:
            val = str(self.arg1)
            # Ignore redundant casts
            if self.op == INT and val[-4:] != "int)":
                toRet += '(' + str(self.arg1) + ')::int'
            elif self.op == FLOAT and val[-6:] != "float)":
                toRet += '(' + str(self.arg1) + ')::float'
            elif self.op == STRING and val[-4:] != "str)":
                toRet += '(' + str(self.arg1) + ')::str'
            elif self.op == BOOLEAN and val[-5:] != "bool)":
                toRet += '(' + str(self.arg1) + ')::bool'
            else:
                mark('unknown unary operation 2')

        else:
            mark('unknown unary operation 3')

        return toRet

    def ast_print(self):
        toRet = '' + self.indent * '| '

        if self.op in {NOT, MINUS}:
            if self.op == NOT:
                toRet += '!'
            elif self.op == MINUS:
                toRet += '-'
            else:
                mark('unknown unary operation 1')

            toRet += self.arg1.ast_print()

        elif self.op in {INT, FLOAT, STRING, BOOLEAN}:
            if self.op == INT:
                toRet += 'int('
            elif self.op == FLOAT:
                toRet += 'float('
            elif self.op == STRING:
                toRet += 'str('
            elif self.op == BOOLEAN:
                toRet += 'bool('
            else:
                mark('unknown unary operation 2')
            toRet += str(self.arg1) + ')'

        else:
            mark('unknown unary operation 3')

        return toRet

    def eval(self):
        if self.op == NOT:
            return BOOL
        elif self.op == MINUS:
            return self.arg1.eval()
        elif self.op == INT:
            return INT
        elif self.op == FLOAT:
            return FLOAT
        elif self.op == STRING:
            return STRING
        elif self.op == BOOLEAN:
            return BOOL
        mark('unknown unary operand type')

class SepNode:
    def __init__(self,lhs,op,rhs):
        self.stmts, self.indent = [], 0
        for i in range(len(lhs)):
            self.stmts.append(AssignNode(lhs[i],op,rhs[i]))

    def ast_print(self):
        toRet = '' + self.indent * '| '
        toRet += self.stmts[0].ast_print()
        for expr in self.stmts[1:]:
            toRet += '\n' + (self.indent + 1) * '| ' + expr.ast_print()
        return toRet

class IfNode:
    def __init__(self,cond,stmt_true,stmt_false):
        self.typ, self.indent = IF, 0

        self.cond = cond
        self.stmt_true  = stmt_true
        self.stmt_false = stmt_false

    def ast_print(self):
        toRet = self.indent * '| '

        if self.stmt_true.typ == BLOCK:
            self.stmt_true.indent = self.indent
        toRet += 'if ' + self.cond.ast_print() + ' then ' + self.stmt_true.ast_print()
        if self.stmt_false != None:
            if self.stmt_false.typ == BLOCK:
                self.stmt_false.indent = self.indent
            toRet += '\n' + (self.indent * '| ') + 'else ' + self.stmt_false.ast_print()
        return toRet

class PrintNode:
    def __init__(self,expr):
        self.typ, self.indent = PRINT, 0
        self.expr = expr

    def ast_print(self):
        toRet = self.indent * '| '
        toRet += 'print ' + self.expr.ast_print()
        return toRet

class LoopNode:
    def __init__(self,cond,loop_start,loop_end,loop_body):
        self.typ, self.indent = LOOP, 0
        self.cond = cond
        self.loop_start = loop_start
        self.loop_end = loop_end
        self.loop_body = loop_body

    def ast_print(self):
        toRet = self.indent * '| '
        toRet += 'for ( ' + self.loop_start.ast_print() + ' ; ' + self.cond.ast_print() + ' ; ' + self.loop_end.ast_print() + ') do '
        if self.loop_body != None:
            if self.loop_body.typ != BLOCK:
                self.loop_body.indent = self.indent + 1
                toRet += '\n'
            else:
                self.loop_body.indent = self.indent
        toRet += self.loop_body.ast_print()
        return toRet

class AssignNode:
    def __init__(self,var,op,val):
        self.typ, self.indent = ASSIGN, 0
        self.var = var
        self.op = op
        self.val = val

    def ast_print(self):
        toRet = self.indent * '| ' + self.var.ast_print() + ' '

        if self.op == PLUS:
            toRet += '+'
        elif self.op == MINUS:
            toRet += '-'
        elif self.op == MULT:
            toRet += '*'
        elif self.op == MOD:
            toRet += '%'
        elif self.op == DIV:
            toRet += '/'
        elif self.op == EQ:
            pass
        else:
            mark('unknown assignment subtype')

        toRet += '= ' + self.val.ast_print()
        return toRet

class ExitNode:
    def __init__(self):
        self.typ, self.indent = EXIT, 0
    def ast_print(self):
        return self.indent * '| ' + 'EXIT'

class ParamNode:
    '''A list of identifiers'''
    def __init__(self,vars):
        self.typ, self.indent = PARAM, 0
        self.vars = vars

    def ast_print(self):
        toRet = '' #self.indent * '| ' #self.var.ast_print()
        for var in self.vars:
            toRet += var.ast_print() + ', '
        return toRet[:-2]

class FuncDefNode:
    def __init__(self,out,params,body):
        self.typ, self.indent = FUNC_DEF, 0
        self.params = params # parameters of the function
        self.out = out # return identifier of the function
        self.body = body # body of the function

    def ast_print(self):
        toRet = self.indent * '| '
        toRet += 'return ' + self.out.ast_print() + ' with ' + self.params.ast_print() + ' from '
        if self.body != None:
            if self.body.typ != BLOCK:
                self.body.indent = self.indent + 1
                toRet += '\n'
            else:
                self.body.indent = self.indent
        toRet += self.body.ast_print()
        return toRet

    def eval(self):
        return IDENT

class ArgNode:
    '''A list of expressions'''
    def __init__(self,exprs):
        self.typ, self.indent = PARAM, 0
        self.exprs = exprs

    def ast_print(self):
        toRet = '' #self.indent * '| ' #self.var.ast_print()
        for expr in self.exprs:
            toRet += expr.ast_print() + ', '
        return toRet[:-2]

class FuncCallNode:
    def __init__(self,name,args):
        self.typ, self.indent = FUNC_DEF, 0
        self.name = name # variable which stores the function
        self.args = args # list of arguments

    def ast_print(self):
        toRet = self.indent * '| '
        toRet += self.name.ast_print() + ' call with ' + self.args.ast_print()
        return toRet
    
    def eval(self):
        return IDENT

class BlockNode:
    def __init__(self,block):
        self.typ, self.indent = BLOCK, 0
        self.block = block

    def ast_print(self):
        toRet =  '{\n'
        for line in self.block:
            line.indent = self.indent + 1
            toRet += line.ast_print() + '\n'
        toRet += (self.indent * '| ') + '}'

        return toRet

    # Required for assembler
    # def __iter__(self):
    #     self._i = 0
    #     return self
    # def __next__(self):
    #     if self._i >= len(self.block):
    #         raise StopIteration
    #     self._i += 1
    #     return self.block[self._i-1]
    # def __len__(self):
    #     return len(self.block)
