# NGL Speed Assembler

from ngl_s_sc import PLUS, MINUS, MULT, DIV, MOD, AND, OR, EQ, LT, GT, NOT, INPUT, COLON, LINEEND, LPAREN, RPAREN, LCURLY, RCURLY, BOOL, NUMBER, RAW_STRING, IDENT, IF, ELSE, PRINT, LOOP, EXIT, BLOCK, ASSIGN, INT, FLOAT, STRING, BOOLEAN, EOF, mark
import ngl_s_ast as AST
import ngl_s_t as TS

# TODO: Preprocess AST for variables
# TODO: Ability to secifiy how 'deep' to assemble
# TODO: Ability to create lines with specific data, not JUST a node
    # TODO: 1 function takes a node and preps it for line creation and a second function actually writes the line
# TODO: Assembler takes only block nodes and line builders take StmtNodes
# TODO: Static functions for common tasks
# TODO: Define state variables
    # TODO: Way to save and load state variables
# TODO: Ability to stop midway through assembly for special logic (input)
# TODO: special function for declaring and deleting old type vars as needed
# TODO: Way to determine type from calculations
# TODO: Automatic casting of output type if it isnt proper? -> or delete old val?
# TODO: special function which will just find identifiers
# TODO: Footer assembler must be able to handle changes in size of `additional`
# TODO: Footer assembly should be performed inline instead of at the end
# TODO: For nested if stmts (if stmt in else branch)
# TODO: Optimizations
    # If statements without else branch

def assemble_init(ast):
    global vars, additional, add_i
    vars = {} # Declared variables
    additional = {} # Jump labels as indexes and the ast to place at the jump
    add_i = 0

    if type(ast) not in {list, tuple}:
        mark('assembler requires ast node list')

    src  = assemble(ast) + '\nquit;'
    back = footer()
    return src + back

def assemble(ast):
    # Takes in a list of commands or a BlockNode and converts all nodes to NGL code
    global vars, additional, add_i
    line = ''
    for t,node in enumerate(ast):

        if type(node) == AST.AssignNode or type(node) == AST.SepNode:
            if type(node) == AST.AssignNode:
                stmts = [node]
            else:
                stmts = node.stmts

            for i, subnode in enumerate(stmts):
                line += createAssignLine(subnode)
                if not len(stmts) == 1 and i != len(stmts)-1:
                    line += '\n'

        elif type(node) == AST.PrintNode:
            line += createPrintLine(node)

        elif type(node) == AST.ExitNode:
            line += createExitLine(node)

        elif type(node) == AST.IfNode:
            line += createIfLine(node)

        elif type(node) == AST.LoopNode:
            line += createLoopLine(node)

        elif type(node) == AST.BlockNode:
            line += assemble(node.block)


        if not len(ast) == 1 and t != len(ast)-1:
            line += '\n'

        # if line != '' and type(node) != AST.BlockNode:
        #     print(line)

    return line # TODO: Always add newline at the end?

def footer():
    global vars, additional, add_i
    if len(additional) == 0: return ''
    line = '\n' * 2
    for i in range(0,add_i):
        line += 'true'+str(i)+':\n'

        try:    node = additional[i] # Loops cause gaps
        except KeyError:    continue
        line += assemble(node) +'\n'

        line += 'goto' +' '+ 'back'+str(i) +';'

        if not len(additional) == 1 and i != len(additional):
            line += '\n'

    return line


def createDelLine(node):
    global vars, additional, add_i
    return 'del' +' '+ str(node.var) + ';\n'

def createAssignLine(node):
    global vars, additional, add_i

    var = str(node.var) # Name of variable for code
    val = str(node.val) # Value to assign to variable
    n_typ = node.val.eval() # Type expression will evaluate to
    line = '' # NGL Line that represents the node

    if n_typ == INPUT:
        raise Exception('not implemented')
    # if final type is a variable, find type of the variable
    if n_typ == IDENT:
        n_typ = vars[val]

    if var in vars:
        if vars[var] != n_typ: # type reassign
            # Delete old NGL variable and then create a new one
            line += createDelLine(node)
            cmd = 'var'
            vars[var] = n_typ
        else:
            cmd = 'set'
    else:
        cmd = 'var'
        vars[var] = n_typ

    # Handles special assignments
    if node.op == PLUS:
        prefix = var + ' +'
    elif node.op == MINUS:
        prefix = var + ' -'
    elif node.op == MULT:
        prefix = var + ' *'
    elif node.op == MOD:
        prefix = var + ' %'
    elif node.op == DIV:
        prefix = var + ' /'
    else:
        prefix = None

    # Convert token to NGL type
    if n_typ == INT:
        typ = 'int'
    elif n_typ == FLOAT:
        typ = 'float'
    elif n_typ == STRING:
        typ = 'str'
    elif n_typ == BOOL:
        typ = 'bool'
    else:
        mark('unknown token type 1'); print(n_typ)

    if prefix and cmd =='var':
        if n_typ == INT:
            line += cmd +' '+ var +'::'+ typ +' '+ str(0) + ';\n'
        elif n_typ == FLOAT:
            line += cmd +' '+ var +'::'+ typ +' '+ str(0.0) + ';\n'
        elif n_typ == STRING:
            line += cmd +' '+ var +'::'+ typ +' '+ '\'\'' + ';\n'
        elif n_typ == BOOLEAN:
            line += cmd +' '+ var +'::'+ typ +' '+ 'false' + ';\n'
        cmd = 'set'

    # Construct NGL line
    line += cmd +' '+ var + ('::' + typ if cmd == 'var' else '') +' '+ (prefix + ' ' if prefix else '') + val + ';'
    return line

def createIfLine(node):
    global vars, additional, add_i
    loc_i = add_i # Save in event of nested ifs
    add_i += 1
    line = ''

    old_vars = dict(vars) # Need to detect new variables inside the loop to avoid multiple declarations
    if node.stmt_true != None:
        stmt_true = assemble([node.stmt_true]) + '\n'
    if node.stmt_false != None:
        stmt_false = assemble([node.stmt_false]) + '\n'
    # Find all new vars
    new_vars = { k : vars[k] for k in set(vars) - set(old_vars) }
    # Roll back
    if len(new_vars) > 0:
        for new_var in new_vars:
            n_typ = new_vars[new_var]
            if n_typ == INT:
                typ = 'int'
            elif n_typ == FLOAT:
                typ = 'float'
            elif n_typ == STRING:
                typ = 'str'
            elif n_typ == BOOL:
                typ = 'bool'
            else:
                mark('unknown token type 2')

            if n_typ == INT:
                line += 'var' +' '+ new_var +'::'+ typ +' '+ str(0) + ';\n'
            elif n_typ == FLOAT:
                line += 'var' +' '+ new_var +'::'+ typ +' '+ str(0.0) + ';\n'
            elif n_typ == STRING:
                line += 'var' +' '+ new_var +'::'+ typ +' '+ '\'\'' + ';\n'
            elif n_typ == BOOLEAN:
                line += 'var' +' '+ new_var +'::'+ typ +' '+ 'false' + ';\n'

        # Regenerate lines
        if node.stmt_true != None:
            stmt_true = assemble([node.stmt_true]) + '\n'
        if node.stmt_false != None:
            stmt_false = assemble([node.stmt_false]) + '\n'

    cond = str(node.cond)
    line += 'if' +' '+ (cond if cond[-5:] == 'bool)' else cond + '::bool') +' true'+str(loc_i) +';\n'
    if node.stmt_false != None:
        line += stmt_false

    if node.stmt_true != None:
        line += 'goto back'+str(loc_i)+';\ntrue'+str(loc_i) +':\n'
        line += stmt_true
    else:
        line += 'true'+str(loc_i) +':\n'

    line += 'back'+str(loc_i)+':'

    # additional[loc_i] = [node.stmt_true];
    return line

def createPrintLine(node):
    global vars, additional, add_i
    return 'print ' + str(node.expr) + ';'

def createExitLine(node):
    global vars, additional, add_i
    return 'quit;'

def createLoopLine(node):
    global vars, additional, add_i
    loc_i = add_i # Save in event of nested ifs
    add_i += 1

    start, body, end = None, None, None
    line = ''
    if node.loop_start != None:
        start = assemble([node.loop_start]) + '\n'

    old_vars = dict(vars) # Need to detect new variables inside the loop to avoid multiple declarations
    if node.loop_body != None:
        body = assemble([node.loop_body]) + '\n'
    if node.loop_end != None:
        end = assemble([node.loop_end]) + '\n'
    # Find all new vars
    new_vars = { k : vars[k] for k in set(vars) - set(old_vars) }
    # Roll back

    if len(new_vars) > 0:
        for new_var in new_vars:
            n_typ = new_vars[new_var]
            if n_typ == INT:
                typ = 'int'
            elif n_typ == FLOAT:
                typ = 'float'
            elif n_typ == STRING:
                typ = 'str'
            elif n_typ == BOOL:
                typ = 'bool'
            else:
                mark('unknown token type 2')

            if n_typ == INT:
                line += 'var' +' '+ new_var +'::'+ typ +' '+ str(0) + ';\n'
            elif n_typ == FLOAT:
                line += 'var' +' '+ new_var +'::'+ typ +' '+ str(0.0) + ';\n'
            elif n_typ == STRING:
                line += 'var' +' '+ new_var +'::'+ typ +' '+ '\'\'' + ';\n'
            elif n_typ == BOOLEAN:
                line += 'var' +' '+ new_var +'::'+ typ +' '+ 'false' + ';\n'

        # Regenerate lines
        if node.loop_body != None:
            body = assemble([node.loop_body]) + '\n'
        if node.loop_end != None:
            end = assemble([node.loop_end]) + '\n'

    if start != None:
        line += start
    line += 'loop'+str(loc_i)+':\n'
    line += 'if' +' >< '+ str(node.cond) +'::bool '+ 'finish'+str(loc_i) +';\n'
    if body != None:
        line += body
    if end != None:
        line += end
    line += 'goto' +' '+ 'loop'+str(loc_i)+';\n'

    line += 'finish'+str(loc_i)+':'
    return line

def convert(fname):
    lst = TS.translate(fname) # Get AST
    for node in lst:
        print(node.ast_print())
    src = assemble_init(lst) # Get NGL source code
    return src

def error():
    return TS.SC.error

if __name__ == '__main__':
    fname = 'usr'
    print(convert(fname))
    print('=====')

    # for stmt in lst:
    #     print(stmt.str_old())
