# NGL Speed NGL Assembler 2.0

import ngl_s_ast2 as AST
import ngl_s_g as TS
from typing import List, Tuple, Dict, Any

class FuncData:
		ID = 0

		def __init__(self, function: AST.FunctionDef):
			assert isinstance(function, AST.FunctionDef)
			
			self.params = function.params
			self.retn = function.retn
			self.body = function.body
			self.id = FuncData.ID

			FuncData.ID += 1

		def getReturnType(self):
			return self.retn
		def getID(self):
			return self.id
		def getParams(self):
			return self.params
		def getBody(self):
			return self.body

		def getCode(self, args: AST.Argument | None):
			assert isinstance(args, AST.Argument) or args is None

			p = self.params
			a = args
			while (p is not None and a is not None):
				assert p.typeEval() == a.typeEval()
				p = p.next
				a = a.next

			i = 0
			m = {}
			variables = self.body.findall(AST.Variable, [])
			for v in variables:
				# If name is assigned, use it
				if v.name.value in m:
					v.name.value = m[v.name.value]
				# If name hasn't been assigned, do so
				else:
					v.name.value = f'f{self.id}arg{i}'
					i += 1

			print(self.body.pprint())

			return 'Done?'


class VarData:
	ID = 0
	def __init__(self, variable: AST.Variable):
		assert isinstance(variable, AST.Variable)
		
		self.name = variable.getName()
		self.type = variable.typeEval()
		self.created = False
		self.id = VarData.ID

		VarData.ID += 1

	def getName(self) -> str:
		return self.name
	def getType(self) -> AST.DataType:
		return self.type
	def isCreated(self) -> bool:
		return self.created
	def getID(self) -> int:
		return self.id

	def __repr__(self):
		return self.pprint()
	def pprint(self) -> str:
		return f'{self.name}{self.id}({repr(self.type)},{self.created})'

class Assembler():
	# Counters for temporary assignments and labels
	count_label = 0
	count_param = 0

	@staticmethod
	def getIDNumber() -> int:
		Assembler.count_label += 1
		return Assembler.count_label - 1

	def __init__(self, start_vars = {}, start_funcs = {}): #, program: AST.Block):

		# assert isinstance(program, AST.Block)
		# self.program = program # input AST to translate

		self.main:   List[str] = [] # main result of the assembly (main code, true branches, assignments, exits, prints)
		self.header: List[str] = [] # header of the result assembly (function bodies)
		self.footer: List[str] = [] # footer of the result assembly (false branches)
		
		self.var_types: Dict[str, VarData]  = start_vars # track variable types
		self.func_data: Dict[str, FuncData] = start_funcs # track function data (body, return type, parameters)

	def assemble(self, program: AST.Block | None):

		main, head, foot = self.assembleProgram(program)
		return ['goto _main;'] + head + ['_main:'] + main + foot 

	def assembleProgram(self, program: AST.Block | None):
		if program is None:
			return [], [], []

		assert isinstance(program, AST.Block)

		self._fillVariables(program)
		self._assembleBlock(program)

		return self.main, self.header, self.footer

	def _fillVariables(self, program: AST.Block):

		all_assigns: List[AST.Assignment] = program.findall(AST.Assignment, [])

		for assignment in all_assigns:

			# Simple Assignment
			if assignment.op == AST.OpType.EQ:
				self.var_types[assignment.var.getName()] = VarData(assignment.var)
				if assignment.var.typeEval() == AST.DataType.FUNC:
					self.func_data[assignment.var.getName()] = FuncData(assignment.expr)

			# Shorthand Assignment
			else:
				# Ensure _variable_ exists
				assert assignment.var.getName() in self.var_types
				# Ensure types are compatible
				assert AST.BinOp.checkType(assignment.op, assignment.var, assignment.var) != AST.DataType.NONE


	def _assembleBlock(self, blocks: AST.Block):
		
		for block in blocks:
			stmt = block.statement
			match type(stmt):
				case AST.Assignment:
					self._assembleAssignment(stmt)
				case AST.IfElse:
					self._assembleIfElse(stmt)
				case AST.Print:
					self._assemblePrint(stmt)
				case AST.Exit:
					self._assembleExit(stmt)
				case AST.ForLoop:
					self._assembleForLoop(stmt)
				case _ as thing:
					print(f'Unknown case: {stmt}')

	def _assembleAssignment(self, assignment_stmt: AST.Assignment, ):
		assert isinstance(assignment_stmt, AST.Assignment)
		
		lines: List[str] = [] # All lines to add. Added to self.main
		line = '' # Current line being worked on. Added to lines
		header: List[str] = [] # Lines to add to the header. Function calls
		
		# Variable name being worked with
		var_name = assignment_stmt.var.getName()

		# Saved variable data
		variable = self.var_types[var_name]
		# Data being drawed upon
		var_type = assignment_stmt.var.typeEval()

		if var_type == AST.DataType.FUNC:
			print('NOT IMPLEMENTED - ASSIGNMENT : FUNCTION DEFINITION')
			
			print(self.func_data[var_name].getCode(None))
			quit()

			return

		# If there is a type incompatibility, we need to reassign the variable
		if var_type != variable.getType():
			raise NotImplementedError(f'Type reassignment: {var_type} -> {variable.getType()}')

		# If variable is already created, we `set` its value
		if variable.isCreated():
			if assignment_stmt.isShorthand():
				line += f'set {var_name} {var_name}{assignment_stmt.op.asmprint()}'
			else:
				line += f'set {var_name} '
		# Otherwise, we create it with `var` and flag that it has been created
		else:
			# If we have an uncreated variable, but do a shorthand assignment, we need to create it
			if assignment_stmt.isShorthand():
				line += f'var {var_name}::{var_type.asmprint()} {Assembler._defaultValue(var_type)};'
				lines.append(line)
				line = f'set {var_name} {var_name}{assignment_stmt.op.asmprint()}'

			else:
				line += f'var {var_name}::{var_type.asmprint()} '
			variable.created = True

		# Add the value
		if isinstance(assignment_stmt.expr, AST.FunctionCall):
			print('NOT IMPLEMENTED - ASSIGNMENT : FUNCTION CALL')
			return

		line += f'{assignment_stmt.expr.asmprint()};'
		lines.append(line)

		self._addToMain(lines)

	def _assembleIfElse(self, ifelse_stmt: AST.IfElse):
		assert isinstance(ifelse_stmt, AST.IfElse)

		inline: List[str] = [] # Lines to add to main (condition and else block)
		header: List[str] = [] # Lines to add to header (none)
		# footer: List[str] = [] # Lines to add to footer (if block)

		my_id = Assembler.getIDNumber() # ID of this if-else statement's labels

		# If-else conditions. Convert to bool if required
		if ifelse_stmt.expr.typeEval() != AST.DataType.BOOL:
			condition = (AST.UnOp(AST.OpType.CAST_BOOL, ifelse_stmt.expr)).asmprint()
		else:
			condition = ifelse_stmt.expr.asmprint()

		# String code for the condition
		conditionCode = f'if >< {condition} if_false{my_id};'

		# List code for if block
		# todo : remove any creations for vars inside the block
		inlineASM = Assembler(self.var_types, self.func_data)
		inline_m, inline_h, inline_f = inlineASM.assembleProgram(ifelse_stmt.ifBlock) # can be empty array

		# List code for else block
		footASM = Assembler(self.var_types, self.func_data)
		foot_m, foot_h, foot_f = footASM.assembleProgram(ifelse_stmt.elseBlock) # can be empty array

		# Add the condition code to main
		inline.append(conditionCode)

		# Add inline (true) code
		if inline_h is not []:	header.extend(inline_h)
		if inline_m is not []:
			inline.extend(inline_m)
			# Only need end if there is an else clause
			inline.append(f'goto if_end{my_id};')
		if inline_f is not []:	inline.extend(inline_f)

		# Add end if inline declaration (only required if there is an else clause)
		# if foot_m is not []: 
		
		
		# Add footer (false)
		if foot_h is not []:		header.extend(foot_h)
		if foot_m is not []:
			inline.append(f'if_false{my_id}:')
			inline.extend(foot_m)
			inline.append(f'goto if_end{my_id};')
		if foot_f is not []:		inline.extend(foot_f)

		inline.append(f'if_end{my_id}:')
		
		self._addToMain(inline)
		# note WE dont add anything to header
		# note BUT, anything declared in the branches must be added
		self._addToHeader(header) 
		# self._addToFooter(footer)

	def _assembleExit(self, exit_stmt: AST.Exit):
		assert isinstance(exit_stmt, AST.Exit)

		self._addToMain(['quit;'])

	def _assemblePrint(self, print_stmt: AST.Print):
		assert isinstance(print_stmt, AST.Print)

		self._addToMain([f'print {print_stmt.expr.asmprint()};'])

	def _assembleForLoop(self, forloop_stmt: AST.ForLoop):
		assert isinstance(forloop_stmt, AST.ForLoop)

		inline: List[str] = [] # Loop init, condition, body and step
		header: List[str] = [] # 
		footer: List[str] = [] # 

		my_id = Assembler.getIDNumber()

		if forloop_stmt.condition.typeEval() != AST.DataType.BOOL:
			condition = (AST.UnOp(AST.OpType.CAST_BOOL, forloop_stmt.condition)).asmprint()
		else:
			condition = forloop_stmt.condition.asmprint()
		conditionCode = f'if >< {condition} for_end{my_id};'

		initASM = Assembler(self.var_types, self.func_data)
		init_m, init_h, init_f = initASM.assembleProgram(forloop_stmt.init) # can be empty array

		stepASM = Assembler(self.var_types, self.func_data)
		step_m, step_h, step_f = stepASM.assembleProgram(forloop_stmt.step) # can be empty array
		
		bodyASM = Assembler(self.var_types, self.func_data)
		body_m, body_h, body_f = bodyASM.assembleProgram(forloop_stmt.body) # can be empty array
		# print(forloop_stmt.body)

		# Write init code
		if (init_h) != []: header.extend(init_h)
		if (init_m) != []: inline.extend(init_m)
		if (init_f) != []: inline.extend(init_f)

		# Write loop label
		inline.append(f'for_start{my_id}:')

		# Write condition code
		inline.append(conditionCode)

		# Write body code
		if (body_h) != []: header.extend(body_h)
		if (body_m) != []: inline.extend(body_m)
		if (body_f) != []: inline.extend(body_f)

		# Write step code
		if (step_h) != []: header.extend(step_h)
		if (step_m) != []: inline.extend(step_m)
		if (step_f) != []: inline.extend(step_f)

		# Create loop
		inline.append(f'goto for_start{my_id};')
		# Create exit label
		inline.append(f'for_end{my_id}:')		

		self._addToMain(inline)
		self._addToHeader(header)
		# self._addToFooter(footer)


	def _addToMain(self, lines: List[str]):
		self.main.extend(lines)
	def _addToHeader(self, lines: List[str]):
		self.header.extend(lines)
	def _addToFooter(self, lines: List[str]):
		self.footer.extend(lines)

	@staticmethod
	def _defaultValue(datatype: AST.DataType) -> str:
		if datatype == AST.DataType.INT:
			return '0'
		elif datatype == AST.DataType.FLOAT:
			return '0.0'
		elif datatype == AST.DataType.STR:
			return "''"
		elif datatype == AST.DataType.BOOL:
			return 'false'
		else:
			raise NotImplementedError(f'Unhandled default value for {datatype}')


def convert(fname):
	ast = TS.translate(fname)

	asm = Assembler() # create assembler
	code = asm.assemble(ast) # assemble program

	# for line in code:
	# 	print('>', line)

	return '\n'.join(code)

if __name__ == '__main__':
	import sys

	if len(sys.argv) < 2:
		fnames = ['./Speed/usr.ngls']
	else:
		fnames = sys.argv[1:]

	for fname in fnames: # For each translation file
			ast = TS.translate(fname) # get AST
			# print(ast.pprint()) # print AST
			print('Starting Assembler')

			asm = Assembler() # create assembler
			code = asm.assemble(ast) # assemble program

			for line in code:
				print('>', line)
