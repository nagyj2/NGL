# NGL Speed AST 2.0

from enum import Enum
from ngl_s_sc import FUNC_DEF, FUNC_CALL, FUNC_END, PARAM, PLUS, MINUS, MULT, DIV, MOD, AND, OR, EQ, LT, GT, NOT, INPUT, COLON, LINEEND, LPAREN, RPAREN, LCURLY, RCURLY, BOOL, NUMBER, RAW_STRING, IDENT, IF, ELSE, PRINT, LOOP, EXIT, BLOCK, ASSIGN, INT, FLOAT, STRING, BOOLEAN, FUNC, EOF, mark
from typing import Union, Type, List

class NodeType(Enum):
	NONE = 0
	EXPRESSION = 1
	STATEMENT = 2

	def __repr__(self):
		if self == NodeType.EXPRESSION:
			return 'EXPRESSION'
		elif self == NodeType.STATEMENT:
			return 'STATEMENT'
		else: #  NodeType.NONE:
			return 'NONE'

class DataType(Enum):
	NONE = 0
	INT = 1
	FLOAT = 2
	STR = 3
	BOOL = 4
	FUNC = 5
	VAR = 6 # represents a found variable const at expr level. Converted to AST.Variable() at stmt level

	def __repr__(self):
		if self == DataType.INT:
			return 'int'
		elif self == DataType.FLOAT:
			return 'float'
		elif self == DataType.STR:
			return 'str'
		elif self == DataType.BOOL:
			return 'bool'
		elif self == DataType.FUNC:
			return 'func'
		elif self == DataType.VAR:
			return 'var'
		else: # self == NodeType.NONE:
			return 'none'
	def asmprint(self):
		return repr(self)

class OpType(Enum):
	PLUS = 1
	MINUS = 2
	MULT = 3
	DIV = 4
	MOD = 5
	POS = 6
	NEG = 7
	LT = 8
	GT = 9
	LE = 10
	GE = 11
	EQ = 12
	NE = 13
	CAST_INT = 14
	CAST_FLOAT = 15
	CAST_STR = 16
	CAST_BOOL = 17
	AND = 18
	OR = 19
	NOT = 20

	def __repr__(self):
		if self == OpType.PLUS:
			return '+'
		elif self == OpType.MINUS:
			return '-'
		elif self == OpType.MULT:
			return '*'
		elif self == OpType.DIV:
			return '/'
		elif self == OpType.MOD:
			return '%'
		elif self == OpType.POS:
			return '+'
		elif self == OpType.NEG:
			return '-'
		elif self == OpType.LT:
			return '<'
		elif self == OpType.GT:
			return '>'
		elif self == OpType.LE:
			return '<='
		elif self == OpType.GE:
			return '>='
		elif self == OpType.EQ:
			return '='
		elif self == OpType.NE:
			return '!='
		elif self == OpType.CAST_INT:
			return '::int'
		elif self == OpType.CAST_FLOAT:
			return '::float'
		elif self == OpType.CAST_STR:
			return '::str'
		elif self == OpType.CAST_BOOL:
			return '::bool'
		elif self == OpType.AND:
			return '&'
		elif self == OpType.OR:
			return '|'
		else: # self == OpType.NE:
			return '!'

	def as_python(self):
		if self == OpType.PLUS:
			return '+'
		elif self == OpType.MINUS:
			return '-'
		elif self == OpType.MULT:
			return '*'
		elif self == OpType.DIV:
			return '/'
		elif self == OpType.MOD:
			return '%'
		elif self == OpType.POS:
			return '+'
		elif self == OpType.NEG:
			return '-'
		elif self == OpType.LT:
			return '<'
		elif self == OpType.GT:
			return '>'
		elif self == OpType.LE:
			return '<='
		elif self == OpType.GE:
			return '>='
		elif self == OpType.EQ:
			return '=='
		elif self == OpType.NE:
			return '!='
		elif self == OpType.CAST_INT:
			return 'int'
		elif self == OpType.CAST_FLOAT:
			return 'float'
		elif self == OpType.CAST_STR:
			return 'str'
		elif self == OpType.CAST_BOOL:
			return 'bool'
		elif self == OpType.AND:
			return 'and'
		elif self == OpType.OR:
			return 'or'
		else: # self == OpType.NE:
			return 'not'

	def asmprint(self):
		return repr(self)

class Translate(Enum):
	class Assignment(Enum):
		SATEMENT = 1
		DEFINITION = 2
		REDEFINITION = 3

	class IfElse(Enum):
		SATEMENT = 1
		CONDITION = 2
		IF = 3
		ELSE = 4

	class ForLoop(Enum):
		SATEMENT = 1
		CONDITION = 2
		INIT = 3
		INCREMENT = 4
		BODY = 5

	class Exit(Enum):
		STATEMENT = 1
	
	class Print(Enum):
		STATEMENT = 1
		ARGUMENT = 2

	class Return(Enum):
		STATEMENT = 1
		ARGUMENT = 2


class Node():
	def __init__(self):
		self.nodeType = NodeType.NONE

	def nodeEval(self) -> NodeType:
		'''Returns the type of AST node.'''
		return self.nodeType

	def __repr__(self):
		return f'Node({self.__class__.__name__})'
	def pprint(self, indent: int = 0, prec: int = 0) -> str:
		return f'{self.__class__.__name__}'

	def as_python(self, indent: int = 0, prec: int = 0) -> str:
		return f'{self.__class__.__name__}'

class Sequence():
	class Iterator():
		def __init__(self, seq: 'Sequence'):
			self.seq = seq
			self.index = 0

		def __next__(self):
			i = 0
			node = self.seq
			while i < self.index:
				node = node.next
				i += 1 
			self.index += 1
			if node is None:
				raise StopIteration
			return node
		
	def __init__(self, selftype, current, next = None):
		self.selftype = selftype
		self.current = current
		self.next = next

		self._refreshSearchable()
	
	def _refreshSearchable(self):
		self.searchable = [self.current, self.next]
	
	def __iter__(self):
		return Sequence.Iterator(self)

	def then(self, other: Node) -> 'Sequence':
		'''Sets the next element in the sequence. Adds to last element in sequence.'''
		
		if not self.next:
			# print(type(other), self.selftype)
			assert not isinstance(other, self.selftype)
			assert type(other) != None
			# assert other.nodeEval() in {NodeType.EXPRESSION, NodeType.STATEMENT}
			# assert type(self) == type(other)

			self.next = self.selftype(other)

		else:
			self.next.then(other)

		return self

	def find(self, typ: Type) -> Union['Sequence', None]:
		'''Finds the first element in the sequence that matches the type.'''
		if self.current.__class__ == typ:	return self
		elif self.next:										return self.next.find(typ)
		else:															return None

	def back(self):
		'''Returns the last element in a sequence.'''
		if self.next:	return self.next.back()
		else:					return self


class Expression(Node):
	def __init__(self):
		super().__init__()
		self.nodeType = NodeType.EXPRESSION
		self.dataType = DataType.NONE
	
	def typeEval(self) -> DataType:
		'''Returns the data type of the expression.'''
		return self.dataType
	def asmprint(self) -> str:
		return 'EXPR_NODE'

class Statement(Node):
	def __init__(self):
		super().__init__()
		self.nodeType = NodeType.STATEMENT
		self.searchable = []

	def _refreshSearchable(self):
		self.searchable = []
	
	def findall(self, typ: Type, found: List['Sequence']) -> List['Sequence']:
		self._refreshSearchable()
		for node in self.searchable:
			# print('Examining:', type(node))
			if isinstance(node, typ):	
				found.append(node)

			# If node has searchables, do so
			if isinstance(node, Statement):
				node.findall(typ, found)

		return found
	

class Const(Expression):
	def __init__(self, typ: DataType, value: Union[int, float, str, bool]):
		super().__init__()
		assert typ in {DataType.INT, DataType.FLOAT, DataType.STR, DataType.BOOL, DataType.VAR, DataType.FUNC}
		
		if typ not in {DataType.VAR, DataType.FUNC}:
			assert type(value) in {int, float, str, bool}
		elif type(typ) == DataType.VAR:
			assert isinstance(value, str)
		else:
			pass
			# assert type(value) in {int, float, str, bool}


		self.dataType = typ
		self.value = value

	def __repr__(self):
		return f"Const({self.dataType} {self.value})"
	def pprint(self, indent: int = 0, prec: int = 0) -> str:
		if self.dataType == DataType.STR:
			return f"'{self.value}'"
		elif self.dataType == DataType.FUNC:
			return f'{self.value.pprint(indent)}'
		return f'{self.value}'
	def asmprint(self, indent: int = 0, prec: int = 0) -> str:
		if self.dataType == DataType.STR:
			return f"'{self.value}'"
		elif self.dataType == DataType.FUNC:
			raise NotImplementedError('Cannot asmprint function') # return f'{self.value.asmprint(indent)}'
		return f'{self.value}'

	def as_python(self, indent: int = 0, prec: int = 100) -> str:
		if self.dataType == DataType.STR:
			return f"'{self.value}'"
		elif self.dataType == DataType.FUNC:
			return f'{self.value}()'
		return f'{self.value}'

class Variable(Expression):
	def __init__(self, typ: DataType, name: Const):
		super().__init__()
		assert typ in {DataType.INT, DataType.FLOAT, DataType.STR, DataType.BOOL, DataType.VAR, DataType.FUNC} # todo : disallow DataType.VAR. Need way to track type in AST generator?
		assert isinstance(name, Const) and name.dataType == DataType.STR

		self.dataType = typ
		self.name = name

	def getName(self):
		return self.name.value

	def __repr__(self):
		return f"Variable({self.dataType} {self.name})"
	def pprint(self, indent: int = 0, prec: int = 0) -> str:
		return f'{self.name.pprint()[1:-1]}::{repr(self.dataType)}'
	def asmprint(self, indent: int = 0, prec: int = 0) -> str:
		return f'{self.name.asmprint()[1:-1]}'

	def as_python(self, indent: int = 0, prec: int = 0) -> str:
		return f'{self.name.as_python()[1:-1]}'

class Input(Const):
	def __init__(self):
		super().__init__(DataType.STR, '')

	def __repr__(self):
		return f"Input({self.dataType})"
	def pprint(self, indent: int = 0, prec: int = 0) -> str:
		return f'input()'
	def asmprint(self, indent: int = 0, prec: int = 0) -> str:
		raise NotImplementedError('Cannot asmprint input')

	def as_python(self, indent: int = 0, prec: int = 0) -> str:
		return f'input()'


class Block(Statement, Sequence):
	@property
	def statement(self):
		return self.current
	
	@statement.setter
	def statement(self, value):
			self.current = value

	def __init__(self, statement: Statement, next: Union[Statement, None] = None):
		Statement.__init__(self)
		Sequence.__init__(self, selftype=Block, current=statement, next=next)

		assert statement.nodeEval() in {NodeType.STATEMENT}
		assert statement == None or statement.nodeEval() in {NodeType.STATEMENT}

	def __repr__(self):
		return f'Block({self.statement}' + (f'\n{self.next})' if self.next != None else ')')
	def pprint(self, indent: int = 0, prec: int = 0) -> str:
		return f'{self.statement.pprint(indent)}' + (f'\n{self.next.pprint(indent)}' if self.next != None else '')

	def as_python(self, indent: int = 0, prec: int = 0) -> str:
		# Need to do some gymnastics to prevent empty lines
		txt = self.statement.as_python(indent, prec)
		if txt != "":
			txt += "\n"
		return txt + (f'{self.next.as_python(indent, prec)}' if self.next != None else '')

class Parameter(Statement, Sequence):
	@property
	def var(self):
		return self.current
	
	@var.setter
	def var(self, value):
			self.current = value

	def __init__(self, var: Variable, next: Union[Variable, None] = None):
		# super().__init__(selftype=Parameter, current=var, next=next)
		Statement.__init__(self)
		Sequence.__init__(self, selftype=Parameter, current=var, next=next)
		
		assert isinstance(var, Variable)
		assert next == None or isinstance(next, Variable)
		# assert var.nodeEval() in {NodeType.EXPRESSION} and var.typeEval() == DataType.VAR
		# assert var == None or var.nodeEval() in {NodeType.EXPRESSION} and var.typeEval() == DataType.VAR

	def __repr__(self):
		return f'Param({self.var}' + (f'\n{self.next})' if self.next != None else ')')
	def pprint(self, indent: int = 0, prec: int = 0) -> str:
		return f'{self.var.pprint()}' + (f', {self.next.pprint()}' if self.next != None else '')

	def as_python(self, indent: int = 0, prec: int = 0) -> str:
		return f'{self.var.as_python()}' + (f', {self.next.as_python()}' if self.next != None else '')

class Argument(Statement, Sequence):
	@property
	def expr(self):
		return self.current
	
	@expr.setter
	def expr(self, value):
			self.current = value

	def __init__(self, expr: Expression, next: Union[Expression, None] = None):
		Statement.__init__(self)
		Sequence.__init__(self, selftype=Argument, current=expr, next=next)

		assert expr.nodeEval() in {NodeType.EXPRESSION}
		assert next == None or next.nodeEval() in {NodeType.EXPRESSION}

	def __repr__(self):
		return f'Arg({self.expr}' + (f'\n{self.next})' if self.next != None else ')')
	def pprint(self, indent: int = 0, prec: int = 0) -> str:
		return f'{self.expr.pprint()}' + (f', {self.next.pprint()}' if self.next != None else '')

	def as_python(self, indent: int = 0, prec: int = 0) -> str:
		return f'{self.expr.as_python()}' + (f', {self.next.as_python()}' if self.next != None else '')

class Alternative(Expression, Sequence):
	@property
	def alternate(self):
		return self.current
	
	@alternate.setter
	def alternate(self, value):
			self.current = value
	
	def __init__(self, expr: Expression, next: Union[Expression, None] = None):
		# super(Expression, self).__init__()
		Expression.__init__(self)
		Sequence.__init__(self, selftype=Alternative, current=expr, next=next)
		
		assert expr.nodeEval() in {NodeType.EXPRESSION}
		assert next == None or next.nodeEval() in {NodeType.EXPRESSION}
		if next:
			assert expr.typeEval() == next.typeEval() # ensure alternative matches type

		self.dataType = expr.typeEval()
		# self.nodeType = NodeType.EXPRESSIONassert expr.typeEval() == next.typeEval()


	def then(self, other: Node) -> 'Alternative':
		'''Sets the next element in the sequence. Adds to last element in sequence.'''
		assert self.typeEval() == other.typeEval() # Ensure alternative has same type

		if not self.next:
			# print(type(other), self.selftype)
			assert not isinstance(other, self.selftype)
			assert type(other) != None
			# assert other.nodeEval() in {NodeType.EXPRESSION, NodeType.STATEMENT}
			# assert type(self) == type(other)

			self.next = self.selftype(other)

		else:
			self.next.then(other)

		return self

	def __repr__(self):
		return f'Alternate({self.alternate}' + (f'\n{self.next})' if self.next != None else ')')
	def pprint(self, indent: int = 0, prec: int = 0, spec = True) -> str:
		if spec:
			return f'({self.alternate.pprint()}' + (f'|{self.next.pprint(spec=False)}' if self.next != None else ')')	
		return f'{self.alternate.pprint()}' + (f'|{self.next.pprint(spec=False)}' if self.next != None else ')')

	def as_python(self, indent: int = 0, prec: int = 0) -> str:
		return f'{self.alternate.as_python()}' + (f' | {self.next.as_python()}' if self.next != None else '')


class FunctionDef(Expression):
	def __init__(self, body: Statement, retn: DataType, params: Union[Parameter, None] = None):
		super().__init__()
		assert body.nodeEval() == NodeType.STATEMENT
		assert isinstance(retn, DataType)
		assert params == None or isinstance(params, Parameter)

		self.params = params
		self.retn = retn
		self.body = body

		self.dataType = DataType.FUNC # retn

	def returntypes(self) -> List[DataType]:
		returns = self.findall(Return)
		types = []
		for node in returns:
			types.append(node.expr.typeEval())
		return types

	def __repr__(self):
		return f'Function({self.params} {self.body} {self.retn})'
	def pprint(self, indent: int = 0, prec: int = 0) -> str:
		return f'function ({self.params.pprint() if self.params else ""}) -> {repr(self.retn)} \n' + f'{self.body.pprint(indent+1)}'

	def as_python(self, indent: int = 0, prec: int = 0) -> str:
		return f'({self.params.as_python() if self.params else ""}):\n{self.body.as_python(indent+1)}'

class FunctionCall(Expression):
	def __init__(self, function: Variable, args: Union[Argument, None] = None):
		super().__init__()
		assert args == None or isinstance(args, Argument)
		assert isinstance(function, Variable)

		self.function = function
		self.args = args

		self.dataType = function.dataType

	def __repr__(self):
		return f'Call({self.function} {self.args})'
	def pprint(self, indent: int = 0, prec: int = 0) -> str:
		return f'call {self.function.pprint()} ({self.args.pprint() if self.args else ""})'

	def as_python(self, indent: int = 0, prec: int = 0) -> str:
		return f'{self.function.as_python()}({self.args.as_python() if self.args else ""})'


class UnOp(Expression):
	def __init__(self, op: OpType, expr: Expression):
		super().__init__()
		assert op in {OpType.POS, OpType.NEG, OpType.CAST_INT, OpType.CAST_FLOAT, OpType.CAST_STR, OpType.CAST_BOOL, OpType.NOT}
		assert expr.nodeEval() in {NodeType.EXPRESSION}

		self.op = op
		self.arg1 = expr

		typ = UnOp.checkType(op, expr)
		if typ == DataType.NONE:
			mark(f'incompatible operation, op:{self.op}, arg1:{self.arg1.dataType}')
			self.dataType = DataType.VAR
		else:
			self.dataType = typ


		self.prec = 10 if self.op in {OpType.CAST_INT, OpType.CAST_FLOAT, OpType.CAST_STR, OpType.CAST_BOOL} else \
								20 #if self.op in {OpType.NOT, OpType.POS, OpType.NEG} else \

	@staticmethod
	def checkType(operation: OpType, arg1: Expression) -> DataType:
		# self.dataType = DataType.INT # todo : calc from input and op
		match (operation, arg1.dataType):
			case (OpType.NOT, _): # Boolean negation
				return DataType.BOOL

			# Arithmetic
			case ((OpType.POS | OpType.NEG), (DataType.INT | DataType.FLOAT) as typ):
				return typ

			# Type casts
			case (OpType.CAST_INT, _): 
				return DataType.INT
			case (OpType.CAST_FLOAT, _): 
				return DataType.FLOAT
			case (OpType.CAST_STR, _): 
				return DataType.STR
			case (OpType.CAST_BOOL, _): 
				return DataType.BOOL

			case _:
				return DataType.NONE

	def __repr__(self):
		return f"UnOp({self.op} {self.arg1})"
	def pprint(self, indent: int = 0, prec: int = 100) -> str:
		if self.op in {OpType.POS, OpType.NEG, OpType.NOT}:
			return (f'(' if self.prec >= prec else '') + f'{repr(self.op)}{self.arg1.pprint(prec = self.prec)}' + (f')' if self.prec >= prec else '')
		return (f'(' if self.prec >= prec else '') + f'{self.arg1.pprint(prec = self.prec)}{repr(self.op)}' + (f')' if self.prec >= prec else '')
	def asmprint(self, indent: int = 0, prec: int = 100) -> str:
		if self.op in {OpType.POS, OpType.NEG, OpType.NOT}:
			return (f'(' if self.prec >= prec else '') + f'{self.op.asmprint()}{self.arg1.asmprint(prec = self.prec)}' + (f')' if self.prec >= prec else '')
		return (f'(' if self.prec >= prec else '') + f'{self.arg1.asmprint(prec = self.prec)}{self.op.asmprint()}' + (f')' if self.prec >= prec else '')

	def as_python(self, indent: int = 0, prec: int = 0) -> str:
		if self.op in {OpType.CAST_INT, OpType.CAST_FLOAT, OpType.CAST_STR, OpType.CAST_BOOL, OpType.NOT} and type(self.arg1) in {Const, Variable, Input}:
			return (f'(' if self.prec >= prec else '') + f'{self.op.as_python()}({self.arg1.as_python(prec = self.prec)})' + (f')' if self.prec >= prec else '')
		return (f'(' if self.prec >= prec else '') + f'{self.op.as_python()}{self.arg1.as_python(prec = self.prec)}' + (f')' if self.prec >= prec else '')	

class BinOp(Expression):
	def __init__(self, op: OpType, expr1: Expression, expr2: Expression):
		super().__init__()
		assert op in {OpType.PLUS, OpType.MINUS, OpType.MULT, OpType.DIV, OpType.MOD, OpType.LT, OpType.GT, OpType.LE, OpType.GE, OpType.EQ, OpType.NE, OpType.AND, OpType.OR}
		assert expr1.nodeEval() in {NodeType.EXPRESSION}
		assert expr2.nodeEval() in {NodeType.EXPRESSION}

		# Find result type
		typ = BinOp.checkType(op, expr1, expr2)
		# Alter result inputs if necessary
		match (op, expr1.dataType, expr2.dataType):
			case (OpType.PLUS, _, DataType.STR):
				if expr1.dataType != DataType.STR:
					expr1 = UnOp(OpType.CAST_STR, expr1)
			case (OpType.PLUS, DataType.STR, _):
				if expr2.dataType != DataType.STR:
					expr2 = UnOp(OpType.CAST_STR, expr2)
		
		self.op = op
		self.arg1 = expr1
		self.arg2 = expr2

		if typ == DataType.NONE:
			mark(f'incompatible operation, op:{self.op}, arg1:{self.arg1.dataType}, arg2:{self.arg2.dataType}')
			self.dataType = DataType.VAR
		else:
			self.dataType = typ
			 
		self.prec = 30 if self.op in {OpType.MULT, OpType.DIV, OpType.MOD} else \
								40 if self.op in {OpType.PLUS, OpType.MINUS} else \
								50 if self.op in {OpType.EQ, OpType.NE, OpType.LT, OpType.GT, OpType.LE, OpType.GE} else \
								60 if self.op in {OpType.AND} else \
								70 if self.op in {OpType.OR} else \
								80 # OpType.ALTERNATIVE


	@staticmethod
	def checkType(operation: OpType, arg1: Expression, arg2: Expression) -> DataType:
		# self.dataType = DataType.INT # todo: calc from input and op
		match (operation, arg1.dataType, arg2.dataType):
			# Boolean combinators
			case (OpType.AND, _, _): 
				return DataType.BOOL
			case (OpType.OR, _, _): 
				return DataType.BOOL

			# Standard arithmetic
			case ((OpType.PLUS | OpType.MINUS | OpType.MULT), DataType.INT, DataType.INT):
				return DataType.INT
			case ((OpType.PLUS | OpType.MINUS | OpType.MULT | OpType.DIV), (DataType.INT | DataType.FLOAT), (DataType.INT | DataType.FLOAT)):
				return DataType.FLOAT
			case (OpType.MOD, DataType.INT, DataType.INT):
				return DataType.INT

			# String concatenation
			case (OpType.PLUS, DataType.STR, DataType.STR):
				return DataType.STR
			case (OpType.PLUS, DataType.STR, _): # todo: requires extra assember code
				return DataType.STR
			case (OpType.PLUS, _, DataType.STR): # todo: requires extra assember code
				return DataType.STR
			case (OpType.MULT, (DataType.INT | DataType.STR), (DataType.INT | DataType.STR)):
				return DataType.STR

			# Comparisons
			case ((OpType.EQ | OpType.NE), _, _):
				return DataType.BOOL
			case ((OpType.LT | OpType.GT | OpType.LE | OpType.GE), (DataType.INT | DataType.FLOAT), (DataType.INT | DataType.FLOAT)):
				return DataType.BOOL
			case ((OpType.LT | OpType.GT | OpType.LE | OpType.GE), DataType.STR, DataType.STR):
				return DataType.BOOL

			# Default
			case _:
				return DataType.NONE
				# mark(f'incompatible operation, op:{self.op}, arg1:{self.arg1.dataType}, arg2:{self.arg2.dataType}')
				

	def __repr__(self):
		return f'BinOp({self.op} {self.arg1} {self.arg2})'
	def pprint(self, indent: int = 0, prec: int = 100) -> str:
		return (f'(' if self.prec >= prec else '') + f'{self.arg1.pprint(prec = self.prec)}{repr(self.op)}{self.arg2.pprint(prec = self.prec)}' + (f')' if self.prec >= prec else '')
	def asmprint(self, indent: int = 0, prec: int = 100) -> str:
		return (f'(' if self.prec >= prec else '') + f'{self.arg1.asmprint(prec = self.prec)}{self.op.asmprint()}{self.arg2.asmprint(prec = self.prec)}' + (f')' if self.prec >= prec else '')

	def as_python(self, indent: int = 0, prec: int = 100) -> str:
		# print(self.op.as_python(), type(self.arg1), type(self.arg2))
		# if type(self.arg2) is Alternative:
		# 	string = '(' + (f'(' if self.prec >= prec else '') + f'{self.arg1.as_python(prec = self.prec)} {self.op.as_python()} {self.arg2.alternate.as_python(prec = self.prec)}' + (f')' if self.prec >= prec else '')
		# 	for arg in self.arg2.next:
		# 		string += ' or ' + (f'(' if self.prec >= prec else '') + f'{self.arg1.as_python(prec = self.prec)} {self.op.as_python()} {arg.alternate.as_python(prec = self.prec)}' + (f')' if self.prec >= prec else '')
		# 	return string + ')'
		return (f'(' if self.prec >= prec else '') + f'{self.arg1.as_python(prec = self.prec)} {self.op.as_python()} {self.arg2.as_python(prec = self.prec)}' + (f')' if self.prec >= prec else '')
	

class Assignment(Statement):
	def __init__(self, var: Variable, op: OpType, expr: Expression):
		super().__init__()
		# assert var.nodeEval() in {NodeType.EXPRESSION} and var.typeEval() == DataType.VAR
		assert isinstance(var, Variable)
		assert op in {OpType.EQ, OpType.PLUS, OpType.MINUS, OpType.MULT, OpType.DIV, OpType.MOD}
		assert expr.nodeEval() in {NodeType.EXPRESSION}
		# if type(expr) == FunctionDef:
		# 	assert var.typeEval() == expr.dataType
		# else:
		# 	assert var.typeEval() == expr.typeEval()

		self.var = var
		self.op = op
		self.expr = expr

		self._refreshSearchable()

		# todo assert types match

	def _refreshSearchable(self):
		self.searchable = [self.var]

	def isShorthand(self) -> bool:
		return self.op != OpType.EQ

	def __repr__(self):
		return f'Assign({self.var} {self.op} {self.expr})'
	def pprint(self, indent: int = 0, prec: int = 0) -> str:
		return f'|  '*indent + f'{self.var.pprint()} {repr(self.op)}= {self.expr.pprint()}'

	def as_python(self, indent: int = 0, prec: int = 0) -> str:
		if self.var.typeEval() == DataType.FUNC:

			return f'def {self.var.as_python()}{self.expr.as_python()}'
		else:
			if self.op == OpType.EQ:	return f'\t'*indent + f'{self.var.as_python()} = {self.expr.as_python(prec = 100)}'
			else:											return f'\t'*indent + f'{self.var.as_python()} {self.op.as_python()}= {self.expr.as_python(prec = 100)}'

class Declaration(Statement):
	def __init__(self, params: Parameter):
		super().__init__()

		assert type(params) == Parameter

		self.params = params

	def __repr__(self):
		return f'Declaration({self.params} {self.body} {self.retn})'
	def pprint(self, indent: int = 0, prec: int = 0) -> str:
		return f'declare {self.params.pprint()}'

	def as_python(self, indent: int = 0, prec: int = 0) -> str:
		return f''

class IfElse(Statement):
	def __init__(self, expr: Expression, ifBlock: Statement, elseBlock: Union[Statement, None] = None):
		super().__init__()
		assert expr.nodeEval() in {NodeType.EXPRESSION}
		assert ifBlock.nodeEval() in {NodeType.STATEMENT}
		assert elseBlock == None or elseBlock.nodeEval() in {NodeType.STATEMENT}

		self.expr = expr
		self.ifBlock = ifBlock
		self.elseBlock = elseBlock

		self._refreshSearchable()

	def _refreshSearchable(self):
		self.searchable = [self.ifBlock, self.elseBlock]

	def __repr__(self):
		return f'IfElse({self.expr} {self.ifBlock} {self.elseBlock})'
	def pprint(self, indent: int = 0, prec: int = 0) -> str:
		return f'|  '*indent + f'if {self.expr.pprint()} then\n{self.ifBlock.pprint(indent+1) if self.ifBlock != None else ""}' + ('\n' + f'|  '*indent + f'else\n{self.elseBlock.pprint(indent+1)}' if self.elseBlock != None else '')

	def as_python(self, indent: int = 0, prec: int = 0) -> str:
		if self.ifBlock == None:
			mark(f'if-else block without if block')
			self.ifBlock = Pass()
		return f'\t'*indent + f'if {self.expr.as_python()}:\n{self.ifBlock.as_python(indent+1) if self.ifBlock != None else ""}' + ('\n' + f'\t'*indent + f'else:\n{self.elseBlock.as_python(indent+1)}' if self.elseBlock != None else '')

class ForLoop(Statement):
	def __init__(self, condition: Expression, body: Union[Statement, None] = None, init: Union[Statement, None] = None, step: Union[Statement, None] = None):
		super().__init__()
		assert condition.nodeEval() in {NodeType.EXPRESSION}
		assert body == None or body.nodeEval() in {NodeType.STATEMENT}
		assert init == None or init.nodeEval() in {NodeType.STATEMENT}
		assert step == None or step.nodeEval() in {NodeType.STATEMENT}

		self.condition = condition
		self.body = body
		self.init = init
		self.step = step

		self._refreshSearchable()

	def _refreshSearchable(self):
		self.searchable = [self.body, self.init, self.step]

	def __repr__(self):
		return f'ForLoop({self.init} {self.condition} {self.step} {self.body})'
	def pprint(self, indent: int = 0, prec: int = 0) -> str:
		return f'|  '*indent + f'for ({self.init.pprint() if self.init else ""} ; {self.condition.pprint()} ; {self.step.pprint() if self.step else ""}) do\n{self.body.pprint(indent+1) if self.body != None else ""}'

	def as_python(self, indent: int = 0, prec: int = 0) -> str:
		if self.condition == None:
			mark('empty condition')
			self.condition = Pass()
		if self.body == None and self.step == None:
			mark('empty loop body')
			self.body = Pass()
		return (f'{self.init.as_python(indent)}\n' if self.init != None else '') + f'\t'*indent + f'while {self.condition.as_python(prec = 100)}:' + (f'\n{self.body.as_python(indent+1)}' if self.body != None else '') + (f'\n{self.step.as_python(indent+1)}' if self.step != None else '')

class Print(Statement):
	def __init__(self, expr: Expression):
		super().__init__()
		assert expr.nodeEval() in {NodeType.EXPRESSION}

		self.expr = expr
		self._refreshSearchable()

	def __repr__(self):
		return f'Print({self.expr})'
	def pprint(self, indent: int = 0, prec: int = 0) -> str:
		return f'|  '*indent + f'print {self.expr.pprint()}'

	def as_python(self, indent: int = 0, prec: int = 0) -> str:
		return f'\t'*indent + f'print({self.expr.as_python()})'

class Exit(Statement):
	def __init__(self):
		super().__init__()
		self._refreshSearchable()

	def __repr__(self):
		return f'Exit()'
	def pprint(self, indent: int = 0, prec: int = 0) -> str:
		return f'|  '*indent + f'exit'
	
	def as_python(self, indent: int = 0, prec: int = 0) -> str:
		return f'\t'*indent + f'quit()'
		
class Pass(Statement):
	def __init__(self):
		super().__init__()
		self._refreshSearchable()

	def __repr__(self):
		return f'Pass()'
	def pprint(self, indent: int = 0, prec: int = 0) -> str:
		return f'|  '*indent + f'pass'
	
	def as_python(self, indent: int = 0, prec: int = 0) -> str:
		return f'\t'*indent + f'pass'

class Return(Statement):
	def __init__(self, expr: Union[Expression, None]):
		super().__init__()
		assert expr.nodeEval() in {NodeType.EXPRESSION}

		self.expr = expr
		self._refreshSearchable()

	def __repr__(self):
		return f'Return({self.expr})'
	def pprint(self, indent: int = 0, prec: int = 0) -> str:
		return f'|  '*indent + f'return {self.expr.pprint()}'

	def as_python(self, indent: int = 0, prec: int = 0) -> str:
		return f'\t'*indent + f'return {self.expr.as_python()}'


if __name__ == '__main__':

	_n = Variable(DataType.INT, Const(DataType.STR, 'n'))
	_i = Variable(DataType.INT, Const(DataType.STR, 'i'))
	_f = Variable(DataType.STR, Const(DataType.STR, 'f'))
	_b = Variable(DataType.STR, Const(DataType.STR, 'b'))

	_decl = Declaration(Parameter(_n).then(_i).then(_f).then(_b))

	_Fizz = Const(DataType.STR, 'Fizz')
	_Buzz = Const(DataType.STR, 'Buzz')
	_fb = BinOp(OpType.PLUS, _f, _b)

	_0 = Const(DataType.INT, 0)
	_1 = Const(DataType.INT, 1)
	_3 = Const(DataType.INT, 3)
	_5 = Const(DataType.INT, 5)
	_15 = BinOp(OpType.MULT, _3, _5)
	_20 = Const(DataType.INT, 20)
	
	_imod3 = BinOp(OpType.MOD, _i, _3)
	_imod5 = BinOp(OpType.MOD, _i, _5)
	_imod15= BinOp(OpType.MOD, _i, _15)

	_notimod3 = UnOp(OpType.NOT, _imod3)
	_notimod5 = UnOp(OpType.NOT, _imod5)

	_iffizz = IfElse(_notimod3, Print(_f))
	_ifbuzz = IfElse(_notimod5, Print(_b))

	_elsefizzbuzz = Block(_iffizz).then(_ifbuzz)
	_iffizzbuzz = IfElse(_imod15, Print(_fb), _elsefizzbuzz)

	_setfizz = Assignment(_f, OpType.EQ, _Fizz)
	_setbuzz = Assignment(_b, OpType.EQ, _Buzz)
	_seti = Assignment(_i, OpType.EQ, _0)
	_setn = Assignment(_n, OpType.EQ, _20)

	_inci = Assignment(_i, OpType.PLUS, _1)

	_iltn = BinOp(OpType.LT, _i, _n)
	_ieqn = BinOp(OpType.EQ, _i, _n)
	_iltnorieqn = BinOp(OpType.OR, _iltn, _ieqn)

	_foriton = ForLoop(_iltnorieqn, _iffizzbuzz, _seti, _inci)

	_program = 	Block(_decl).then(_setn).then(_setfizz).then(_setbuzz).then(_foriton).then(Exit())

	# print(_program)
	print(_program.pprint())

	lookFor = Variable
	found = _program.findall(lookFor, [])
	if (len(found) > 0):
		print(f'Found: {len(found)} of {lookFor}')
	else:
		print(f'Missing {lookFor}')

