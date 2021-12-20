# NGL Speed AST Generator 2.0

import ngl_s_sc as SC
from ngl_s_sc import FUNC_DEF, FUNC_CALL, FUNC_END, PLUS, MINUS, MULT, DIV, MOD, AND, OR, EQ, NE, LT, GT, GE, LE, CMP_OR, STMT_AND, NOT, INPUT, COLON, LINEEND, LPAREN, RPAREN, LCURLY, COMMA, RCURLY, BOOL, NUMBER, RAW_STRING, INT, FLOAT, STRING, BOOLEAN, DECL_INT, DECL_FLOAT, DECL_STRING, DECL_BOOLEAN, IDENT, IF, ASSIGN, BLOCK, ELSE, PRINT, LOOP, EXIT, EOF, mark, getSym
import ngl_s_ast2 as AST
from copy import deepcopy # todo: offer better copying

FIRSTATOM  = {IDENT, NUMBER, BOOL, RAW_STRING, LPAREN, INPUT, FUNC_CALL}
FOLLOWATOM = {IDENT, NUMBER, BOOL, RAW_STRING, RPAREN, INPUT}

FIRSTSUBATOM  = {INT, FLOAT, STRING, BOOLEAN} | FIRSTATOM
FOLLOWSUBATOM =  FOLLOWATOM

FIRSTEXPR_L6  = {NOT, PLUS, MINUS} | FIRSTSUBATOM
FOLLOWEXPR_L6 = FOLLOWSUBATOM

FIRSTEXPR_L5  = FIRSTEXPR_L6
FOLLOWEXPR_L5 = FOLLOWEXPR_L6

FIRSTEXPR_L4  = FIRSTEXPR_L5
FOLLOWEXPR_L4 = FOLLOWEXPR_L5

FIRSTEXPR_L3  = FIRSTEXPR_L4 #{PLUS, MINUS} | FIRSTEXPR_L3
FOLLOWEXPR_L3 = FOLLOWEXPR_L4

FIRSTEXPR_L2  = FIRSTEXPR_L3
FOLLOWEXPR_L2 = FOLLOWEXPR_L3

FIRSTEXPR_L1  = FIRSTEXPR_L2
FOLLOWEXPR_L1 = FOLLOWEXPR_L2

FIRSTEXPR_L0  = FIRSTEXPR_L1
FOLLOWEXPR_L0 = FOLLOWEXPR_L1

FIRSTEXPR  = {FUNC_DEF} | FIRSTEXPR_L0
FOLLOWEXPR = FOLLOWEXPR_L0

FIRSTSTMT  = {IDENT, IF, PRINT, LOOP, EXIT, LCURLY, DECL_INT, DECL_FLOAT, DECL_STRING, DECL_BOOLEAN}
FOLLOWSTMT = {INPUT, RCURLY} | FOLLOWEXPR

FIRSTLINES  = FIRSTSTMT
FOLLOWLINES = {LINEEND}

FIRSTPROGRAM  = FIRSTLINES
FOLLOWPROGRAM = FOLLOWLINES

STRONGSYMS = {IF, PRINT, LOOP, EXIT, LCURLY, RCURLY, EOF, FUNC_END, DECL_INT, DECL_FLOAT, DECL_STRING, DECL_BOOLEAN}

# Tracks whether the parser is in a function
in_func = False
# Tracts variable types - just used to aid in AST creation! NOT RETURNED
var_scope = []
# Tracks return types of functions - just used to aid in AST creation! NOT RETURNED
functions = {}

def program() -> AST.Block:
	global in_func, var_scope
	if SC.sym not in FIRSTPROGRAM:
		mark('expected valid program start')

	prog = None
	var_scope.append({})

	if SC.sym in FIRSTPROGRAM:
		prog = lines()
	else:
		mark('expected NGLS code')

	itr = prog.back()
	while SC.sym in FIRSTPROGRAM:
		itr.next = lines()
		itr = itr.back()

		# exit func modes if end is found
		if in_func and SC.sym == FUNC_END:
			break

	# If any undeclared (VAR) variables, state they are undeclared
	undeclareds = list(filter(lambda key_val: key_val[1] == AST.DataType.VAR, var_scope[-1].items()))
	if len(undeclareds) > 0:
		mark(f'warning: variables not declared: {undeclareds}')

	var_scope.pop()

	return prog

def lines() -> AST.Block:
	global functions, var_scope
	if SC.sym not in FIRSTLINES:
		mark('expected valid lines start')

	if SC.sym in FIRSTSTMT:
		val = stmt()

		# Possible to assume that the next symbol is a new statement
		# If a lineend, consume. If not, dont worry!
		if SC.sym in STRONGSYMS:
			# Probably not a good idea to allow a poorly formatted program...
			if SC.sym == LINEEND:
				getSym()

		# Cannot assume next symbol represents a new statement
		# If a lineend, consume. If not, PANIC!
		else:
			if SC.sym == LINEEND:
				getSym()
			else:
				print(SC.sym, SC.val)
				mark('expected semicolon')

		if SC.sym in FOLLOWLINES:
			mark('warning: empty line')
			while SC.sym in FOLLOWLINES:
				getSym()

	else:
		mark(f'unknown enum lines: {SC.sym}')

	for var in functions:
		assert var in var_scope[-1]

	return val

def stmt() -> AST.Block:
	if SC.sym not in FIRSTSTMT:
		mark('expected valid stmt start')
	val = None

	if SC.sym == IDENT:
		
		first = True
		while SC.sym == IDENT:
			# Get variable name const
			var_const = AST.Const(AST.DataType.STR, SC.val)
			getSym()

			# Determine type of assignment
			if SC.sym in {EQ, PLUS, MINUS, MULT, DIV, MOD}:
				assign_op = AST.OpType.PLUS if SC.sym == PLUS else \
							AST.OpType.MINUS if SC.sym == MINUS else \
							AST.OpType.MULT if SC.sym == MULT else \
							AST.OpType.DIV if SC.sym == DIV else \
							AST.OpType.MOD if SC.sym == MOD else \
							AST.OpType.EQ
				getSym()

			# Assume regular assignment
			else:
				assign_op = AST.OpType.EQ 
			
			# Get expression
			if SC.sym in FIRSTEXPR:
				value_expr = expr()
			else:
				mark('expected expression')
				value_expr = AST.Const(AST.DataType.INT, 0)

			# Confirm type agreement if variable has been used already
			if var_const.value in var_scope[-1]:

				# If value is a function, grab the return type
				if isinstance(value_expr, AST.FunctionCall):
					if value_expr.function.getName() in functions:
						var_type = functions[value_expr.function.getName()]
					else:
						mark(f'call on non-function type')
						var_type = AST.DataType.VAR

				# Otherwise, grab the variable type
				else:
					# Always assume the previous type is correct
					var_type = var_scope[-1][var_const.value]
				
				# Check if type is correct
				if var_type != value_expr.typeEval():
					# If not, mark and insert a cast
					mark(f'assigmnent type mismatch: {var_type}!={value_expr}')
					# Non-functions can be simply casted
					if var_type != AST.DataType.FUNC:
						value_expr = AST.UnOp(  AST.OpType.CAST_INT if value_expr.typeEval() == AST.DataType.INT else \
												AST.OpType.CAST_FLOAT if value_expr.typeEval() == AST.DataType.FLOAT else \
												AST.OpType.CAST_STR if value_expr.typeEval() == AST.DataType.STR else \
												AST.OpType.CAST_BOOL, #if value_expr.typeEval() == AST.DataType.INT else \
												value_expr)
					else:
						print('Not implemented!! Cannot cast function easily!!')
						quit()

			# Otherwise, take the type of the expression
			else:
				var_type = value_expr.typeEval()

				if type(val) != AST.Block:
					val = AST.Block(AST.Declaration(AST.Parameter(AST.Variable(var_type, var_const))))
				else:
					val.then(AST.Declaration(AST.Parameter(AST.Variable(var_type, var_const))))

				# Fill out the variable table
				var_scope[-1][var_const.value] = var_type


			# If a function definition, do some trickery
			if isinstance(value_expr, AST.FunctionDef):
				functions[var_const.value] = value_expr.retn
				var_scope[-1][var_const.value] = var_type

				# `+=` and equivalent operators do not work with functions
				if assign_op != AST.OpType.EQ:
					mark('cannot use shorthand assignment operators on a function')
					assign_op = AST.OpType.EQ

			# Add assignment to the block
			if type(val) != AST.Block:
				val = AST.Block(AST.Assignment(AST.Variable(var_type, var_const), assign_op, value_expr))
			else:
				val.then(AST.Assignment(AST.Variable(var_type, var_const), assign_op, value_expr))

			# If undeclared var is found, fill it out
			if var_scope[-1][var_const.value] == AST.DataType.VAR:
				var_scope[-1][var_const.value] = var_type

	elif SC.sym == IF:
		# if statement
		getSym()

		if SC.sym in FIRSTEXPR:
			cond = expr()
		else:
			mark('empty if condition')
			cond = AST.Const(AST.DataType.BOOL, False)

		if SC.sym in FIRSTSTMT:
			true = stmt()
		else:
			true = AST.Pass()

		if SC.sym == ELSE:
			getSym()
			false = stmt()
		else:
			false = None

		val = AST.Block(AST.IfElse(cond,true,false))

	elif SC.sym == PRINT:
		# print stmt
		getSym()
		display = expr()
		val = AST.Block(AST.Print(display))

	elif SC.sym == LOOP:
		# loop stmt
		getSym()
		cond = expr()
		if SC.sym == COLON:
			getSym()
		else:
			mark('expected colon')

		if SC.sym in FIRSTSTMT:
			init = stmt()
		else:
			init = None

		if SC.sym == COLON:
			getSym()
		else:
			mark('expected colon')

		if SC.sym in FIRSTSTMT:
			step = stmt()
		else:
			step = None

		if SC.sym == COLON:
			getSym()
		else:
			mark('expected colon')

		if SC.sym in FIRSTSTMT:
			body = stmt()
		else:
			body = None

		val = AST.Block(AST.ForLoop(cond, body, init, step))

	elif SC.sym == EXIT:
		# print stmt
		getSym()
		if not in_func:
			val = AST.Block(AST.Exit())

		else:
			if SC.sym in FIRSTEXPR:
				retn = expr()
			else:
				mark('missing return value')
			val = AST.Block(AST.Return(retn))

	elif SC.sym == LCURLY:
		# stmt block
		getSym()

		if SC.sym in FIRSTLINES:
			val = lines()
		else:
			val = None
			mark('blocks require at least one line')
			# val = AST.Block(AST.Assignment(AST.Variable(AST.DataType.INT,'_'),AST.DataType.EQ,AST.Const(AST.DataType,0)))
		
		itr = val.back()
		while SC.sym in FIRSTLINES:
			itr.next = lines()
			itr = itr.back()

		if SC.sym == RCURLY:
			getSym()
		else:
			mark('expected closing curly brace')

	elif SC.sym in {DECL_INT, DECL_FLOAT, DECL_STRING, DECL_BOOLEAN}:

		# Find type for declaration
		vartyp =	AST.DataType.INT   if SC.sym == DECL_INT     else \
							AST.DataType.FLOAT if SC.sym == DECL_FLOAT   else \
							AST.DataType.STR   if SC.sym == DECL_STRING  else \
							AST.DataType.BOOL #if SC.sym == DECL_BOOLEAN else \
							# mark('invalid type')
		getSym()

		# Find first variable
		if SC.sym == IDENT:
			varname = AST.Const(AST.DataType.STR, SC.val)
			getSym()
		else:
			varname = AST.Const(AST.DataType.STR, '_')
			mark('expected variable')

		# Create type mapping
		var_scope[-1][varname.value] = vartyp
		# Create variable sequence
		params = AST.Parameter(AST.Variable(vartyp, varname))

		while SC.sym in {IDENT, COMMA}:
			if SC.sym == COMMA:
				getSym()

			# Find next variable
			if SC.sym == IDENT:
				varname = AST.Const(AST.DataType.STR, SC.val)
				getSym()
			else:
				varname = AST.Const(AST.DataType.STR, '_')
				mark('expected variable')

			# Create type mapping
			var_scope[-1][varname.value] = vartyp
			# Create variable sequence
			params.then(AST.Variable(vartyp, varname))

		val = AST.Block(AST.Declaration(params))

	else:
		mark(f'unknown enum stmt: {SC.sym}')
		val = AST.Block(AST.Assignment(AST.Variable(AST.DataType.INT, '_'), AST.Const(AST.DataType.INT, 0)))

	if SC.sym == STMT_AND:
		getSym()
		for extra in stmt():
			val.then(extra.statement)

	return val

def expr() -> AST.Expression:
	global in_func, var_scope, functions
	if SC.sym not in FIRSTEXPR:
		mark('expected valid expr start')
	
	if SC.sym == FUNC_DEF:
		getSym()

		# If a return type is specified, take it
		if SC.sym in {INT, FLOAT, STRING, BOOLEAN}:
			if SC.sym == INT:       retntyp = AST.DataType.INT; getSym()
			elif SC.sym == FLOAT:   retntyp = AST.DataType.FLOAT; getSym()
			elif SC.sym == STRING:  retntyp = AST.DataType.STR; getSym()
			elif SC.sym == BOOLEAN: retntyp = AST.DataType.BOOL; getSym()
			else:
				retntyp = AST.DataType.VAR
				mark('expected return type')

		# Otherwise, find it from the function body
		else:
			retntyp = None

		# todo change formatting to not need this
		if SC.sym == COLON:
			getSym()
		else:
			mark('expected colon')

		if SC.sym in {INT, FLOAT, STRING, BOOLEAN}:
			first = True
			while SC.sym in {INT, FLOAT, STRING, BOOLEAN}:
				if SC.sym == INT:       vartyp = AST.DataType.INT; getSym()
				elif SC.sym == FLOAT:   vartyp = AST.DataType.FLOAT; getSym()
				elif SC.sym == STRING:  vartyp = AST.DataType.STR; getSym()
				elif SC.sym == BOOLEAN: vartyp = AST.DataType.BOOL; getSym()
				else:                   vartyp = AST.DataType.VAR; mark('expected variable type')

				while SC.sym == IDENT:
					varname = AST.Const(AST.DataType.STR, SC.val)
					getSym()

					if first:   params = AST.Parameter(AST.Variable(vartyp, varname)); first = False
					else:       params.then(AST.Variable(vartyp, varname))

		else:
			params = []

		if SC.sym == COLON:
			getSym()
		else:
			mark('expected colon')

		in_func = True

		# Add new scope
		var_scope.append({})

		# Insert params to allow parsing of function body
		for param in params: # param.current = variable
			var_scope[-1][param.current.name.value] = param.current.dataType

		body = program()

		# todo ensure each path has a return statement
		# todo : allow function return inference by finding all return path types

		returns = body.findall(AST.Return, [])

		# Tf there was returns
		if len(returns) >= 1:
			if retntyp == None:
				retntyp = returns[0].expr.typeEval()

		# No returns
		else:
			mark('functions must return a type')
			returns = [AST.Return(AST.Const(AST.DataType.VAR, '_'))]
			if retntyp == None:
				retntyp = AST.DataType.VAR
				

		for typ in returns:
			if typ.expr.typeEval() != retntyp:
				mark(f'return type mismatch: {typ}!={retntyp}')
				retntyp = typ

		# restore state
		in_func = False
		to_find = old_decl

		var_scope.pop()

		# Create node
		val = AST.FunctionDef(body, retntyp, params)

		if SC.sym == FUNC_END:
			getSym()
		else:
			mark('expected function closing brace')

	else:
		val = expr_l0()

	return val

def expr_l0() -> AST.Expression:
	if SC.sym not in FIRSTEXPR_L0:
		mark('expected valid expr_l0 start')

	val = expr_l1()

	if type(val) == AST.Alternative:
		val = _expand_alternatives(val)

	while SC.sym in {AND, OR}:
		op =	AST.OpType.AND if SC.sym == AND else \
				AST.OpType.OR  if SC.sym == OR  else \
				mark('expected AND or OR')
		getSym()
		mod = expr_l1()

		val = _resolve_alternatives(op,val,mod)
		# val = AST.BinOp(op,val,mod)

	if type(val) == AST.Alternative:
			val = _expand_alternatives(val)

	return val

def expr_l1() -> AST.Expression:
	if SC.sym not in FIRSTEXPR_L1:
		mark('expected valid expr_l1 start')

	val = expr_l2()

	if SC.sym in {EQ}:
		op =    AST.OpType.EQ if SC.sym == EQ else \
						mark('expected comparison operator')
		getSym()

		mod = expr_l2()

		# Perform special logic to bubble up alternatives
		val = _resolve_alternatives(op,val,mod)

	return val

def expr_l2() -> AST.Expression:
	if SC.sym not in FIRSTEXPR_L2:
		mark('expected valid expr_l2 start')

	fst = expr_l3()

	chain = False
	while SC.sym in {LT, GT, LE, GE}:
		op =	AST.OpType.LT  if SC.sym == LT  else \
				AST.OpType.GT  if SC.sym == GT  else \
				AST.OpType.LE  if SC.sym == LE  else \
				AST.OpType.GE  if SC.sym == GE  else \
				mark('expected comparison operator')
		getSym()
		snd = expr_l3()

		#todo: add Alternate support
		if type(fst) is AST.Alternative or type(snd) is AST.Alternative:
			mark('alternatives nor supported in comparison ranges')
			if type(fst) is AST.Alternative: fst = fst.alternate
			if type(snd) is AST.Alternative: snd = snd.alternate

		if chain:
			fst = AST.BinOp(AST.OpType.AND, fst, AST.BinOp(op,last,snd))
			last = deepcopy(snd)

		else:
			chain = True
			fst = AST.BinOp(op,fst,snd)
			last = deepcopy(snd)

	return fst

def expr_l3() -> AST.Expression:
	if SC.sym not in FIRSTEXPR_L3:
		mark('expected valid expr_l3 start')

	val = expr_l4()

	while SC.sym in {PLUS, MINUS}:
		op =	AST.OpType.PLUS if SC.sym == PLUS else \
				AST.OpType.MINUS  if SC.sym == MINUS  else \
				mark('expected PLUS or MINUS')
		getSym()

		mod = expr_l4()

		# Perform special logic to bubble up alternatives
		val = _resolve_alternatives(op,val,mod)

	return val

def expr_l4() -> AST.Expression:
	if SC.sym not in FIRSTEXPR_L4:
		mark('expected valid expr_l4 start')

	val = expr_l5()

	while SC.sym in {MULT, DIV, MOD}:
		op =	AST.OpType.MULT if SC.sym == MULT else \
				AST.OpType.DIV  if SC.sym == DIV  else \
				AST.OpType.MOD  if SC.sym == MOD  else \
				mark('expected MULT, DIV or MOD')
		getSym()

		mod = expr_l5()
		
		# Perform special logic to bubble up alternatives
		val = _resolve_alternatives(op,val,mod)

	return val

def expr_l5() -> AST.Expression:
	if SC.sym not in FIRSTEXPR_L5:
		mark('expected valid expr_l5 start')

	val = expr_l6() # A single atom

	first = True
	while SC.sym in {CMP_OR}:
		getSym()
		
		if SC.sym in FIRSTEXPR_L6:
			mod = expr_l6() # A second atom

			if first:	val = AST.Alternative(val).then(mod); first = False
			else:			val.then(mod)
		
		else:
			mark('expected expression')

	return val

def expr_l6() -> AST.Expression:
	if SC.sym not in FIRSTEXPR_L6:
		mark('expected valid expr_l6 start')

	if SC.sym in {NOT, PLUS, MINUS}:
		op =	AST.OpType.NOT if SC.sym == NOT   else \
					AST.OpType.POS if SC.sym == PLUS  else \
					AST.OpType.NEG if SC.sym == MINUS else \
					mark('expected unary operator')
		getSym()
		val = AST.UnOp(op,subatom())
	else:
		val = subatom()

	return val

def subatom() -> AST.Expression:
	if SC.sym not in FIRSTSUBATOM:
		mark('expected valid subatom start')

	if SC.sym == INT:
		getSym(); val = AST.UnOp(AST.OpType.CAST_INT, subatom())
	elif SC.sym == FLOAT:
		getSym(); val = AST.UnOp(AST.OpType.CAST_FLOAT, subatom())
	elif SC.sym == STRING:
		getSym(); val = AST.UnOp(AST.OpType.CAST_STR, subatom())
	elif SC.sym == BOOLEAN:
		getSym(); val = AST.UnOp(AST.OpType.CAST_BOOL, subatom())
	else:
		val = atom()

	if SC.sym in {INT, FLOAT, STRING, BOOLEAN}:
		mark('cast goes before expression')
		getSym()

	return val

def atom() -> AST.Expression:
	global in_func, var_scope
	if SC.sym not in FIRSTATOM:
		mark('expected valid atom start')

	if SC.sym == IDENT:
		# identifier

		# check to see if the variable is already defined
		if SC.val in var_scope[-1]:
			if SC.val in functions:
				typ = functions[SC.val]
			else:
				typ = var_scope[-1][SC.val]

			# todo : how to deal with types?
			value = AST.Variable(typ, AST.Const(AST.DataType.STR, SC.val))
		else:
			# todo : get rid of this if possible
			typ = AST.DataType.VAR
			value = AST.Const(typ, SC.val)
			# Add a 'VAR' type variable. This is a hack to allow for use of vars before they are mentioned in source, particularly for loops
			var_scope[-1][SC.val] = typ
			# mark('undefined variable')
		
		getSym()

	elif SC.sym == NUMBER:
		# int or float
		if isinstance(SC.val, int):
			value = AST.Const(AST.DataType.INT, SC.val)
		elif isinstance(SC.val, float):
			value = AST.Const(AST.DataType.FLOAT, SC.val)
		else:
			mark('expected number')
			value = AST.Const(AST.DataType.INT, 0)
		getSym()

	elif SC.sym == BOOL:
		# true token
		value = AST.Const(AST.DataType.BOOL, True)
		getSym()

	elif SC.sym == RAW_STRING:
		# string
		value = AST.Const(AST.DataType.STR, SC.val)
		getSym()

	elif SC.sym == INPUT:
		# string
		value = AST.Input()
		getSym()

	elif SC.sym == LPAREN:
		# nested expression
		getSym()

		# sub_val = expr()
		# value = AST.Node(BLOCK,sub_val)
		value = expr()

		if SC.sym == RPAREN:
			getSym()
		else:
			mark('expected closing paren')

	elif SC.sym == FUNC_CALL:
		# function call
		getSym()

		if SC.sym == IDENT:
			# If identifier is callable
			if SC.val in functions:
				# todo : differentiate functions and variables in `variables`
				callee = AST.Variable(functions[SC.val], AST.Const(AST.DataType.STR, SC.val))
			else:
				mark('function call on non-function')
				callee = AST.Variable(AST.DataType.FUNC, AST.Const(AST.DataType.STR, SC.val))
			
			getSym()

		else:
			mark('expected function name')
			callee = AST.Const(AST.DataType.STR, '_')

		if SC.sym == COLON:
			getSym()
		else:
			mark('expected colon')

		# Take in arguments
		if SC.sym in FIRSTEXPR:
			# todo : check argument type
			args = AST.Argument(expr())

			while SC.sym in FIRSTEXPR | {COMMA}:
				if SC.sym == COMMA:
					getSym()

				args.then(expr())
		else:
			args = None

		value = AST.FunctionCall(callee, args)

		if SC.sym == FUNC_END:
			getSym()
		else:
			mark('expected function closing brace')

	else:
		mark('invalid enum atom')
		value = None

	return value


def _resolve_alternatives(op: AST.OpType, val: AST.Alternative | AST.Expression, mod: AST.Alternative | AST.Expression) -> AST.Alternative | AST.Expression:
	'''Takes in two ASTs with zero or more being AST.Alternatives and enumerates all possible combinations of the two.'''
	# If an alternative is returned, it should be bubbled up to OR precidence level
	if type(mod) is AST.Alternative or type(val) is AST.Alternative:

		# Determine which is the alternative
		if type(val) == type(mod):
			first = True
			for curr_l in val:
				for curr_r in mod:
					if first: val = AST.Alternative(AST.BinOp(op, deepcopy(curr_l.alternate), deepcopy(curr_r.alternate))); first = False
					else:			val.then(AST.BinOp(op, deepcopy(curr_l.alternate), deepcopy(curr_r.alternate)))

		else:
			if type(val) is AST.Alternative:	orig, other, inv = mod, val, False
			else:															orig, other, inv = val, mod, True # type(mod) is AST.Alternative

			if inv:	val = AST.Alternative(AST.BinOp(op, deepcopy(orig), other.alternate))
			else:		val = AST.Alternative(AST.BinOp(op, other.alternate, deepcopy(orig)))

			for alt in other.next:
				if inv:	val.then(AST.BinOp(op, deepcopy(orig), alt.alternate))
				else:		val.then(AST.BinOp(op, alt.alternate, deepcopy(orig)))

	else:
		val = AST.BinOp(op,val,mod)

	return val

def _expand_alternatives(val: AST.Alternative) -> AST.Expression:
	orig = deepcopy(val)

	val = AST.BinOp(AST.OpType.OR, val.alternate, val.next.alternate)

	if orig.next.next:
		for alt in orig.next.next:
			val = AST.BinOp(AST.OpType.OR, val, alt.alternate)
	return val

def _readsource(fname):
	src = ''
	with open(fname,'r') as reader:
		for line in reader.readlines():
			src += line
	return src

def translate(fname) -> AST.Block:
	src = _readsource(fname)
	SC.init(fname, src)
	prog = program()

	# Add exit if not there
	if not isinstance(prog.back(), AST.Exit):
		prog.then(AST.Exit())

	return prog

if __name__ == '__main__':
	import sys

	if len(sys.argv) < 2:
		fnames = ['./Speed/usr.ngls']
	else:
		fnames = sys.argv[1:]

	for fname in fnames:
		ast = translate(fname)
		print(ast.pprint())

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
