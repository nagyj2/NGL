# NGL Bytecode 2.1 Entities (for Symbol Table)

from copy import deepcopy
from math import log10
import bc2_1_sc as SC
from bc2_1_sc import INT, FLOAT, BOOL, STRING, NULL, ARRAY, LIST, EQ, NE, LT, GT, PLUS, MINUS, MULT, DIV, MOD, EXP, AND, OR, NOT, E_NOT, PRIMATIVE, COLLECTION, mark

class Variable:
	def __init__(self, typ, value): #, const = False):
		if typ not in PRIMATIVE:
			mark('invalid variable primitive')
			self.typ, self.value = NULL, None
		else:
			self.typ = typ
			self.value = Variable._conv(self.typ, value)

	def __getitem__(self, index):
		# Only string variables can be indexed
		if type(index) == Variable:
			index = Variable._conv(INT,index)
		elif type(index) == Collection:
			mark('cannot index with collection')
		if self.typ != STRING:
			mark('variable cannot be indexed')
			return Variable(STRING,'')
		elif index >= len(self.value):
			mark('invalid index')
			return Variable(STRING,'')
		return Variable(STRING,self.value[index])
	def __len__(self):
		if arg.typ in {INT, FLOAT}:
			if arg.value > 0:    	return int(log10(arg.value))+1
			elif arg.value == 0: 	return 1
			else:                	return int(log10(-arg.value))+1 # +1 if you don't count the '-'
		elif arg.typ == STRING:  	return len(arg.value)
		elif arg.typ == BOOL:    	return 1
		else:						return 0

	def __int__(self):
		return Variable._conv(INT,self.value)
	def __float__(self):
		return Variable._conv(FLOAT,self.value)
	def __str__(self):
		return Variable._conv(STRING,self.value)
	def __bool__(self):
		return Variable._conv(BOOL,self.value)

	def __neg__(self):
		# FIX: should use _resolve
		if self.typ == INT:
			return Variable(INT, -self.value)
		elif self.typ == FLOAT:
			return Variable(FLOAT, -self.value)
		elif self.typ == BOOL:
			return Variable(BOOL, not self.value)
		else: # self.typ in {STRING, NULL}:
			mark('invalid negation')
			return Variable(NULL,None)

	def __add__(self, other):
		if type(other) == Variable:
			if self.typ in {INT, FLOAT} and other.typ in {INT, FLOAT}:
				return Variable._resolve(self, PLUS, other)
			elif self.typ == other.typ == STRING:
				return Variable._resolve(self, PLUS, other)
			else:
				print('>',self,self.typ,other,other.typ) 
				raise Exception('not implemented: +')
		else: # Collection
			other_copy = deepcopy(other)
			if other_copy.typ != self.typ:	mark('variable and collection primitive type mismatch')
			elif other_copy.const:			mark('arrays cannot be modified')
			else:                       	other_copy.collect.append(self)
			return other_copy
	def __radd__(self, other):
		return self + other
	def __sub__(self, other):
		if type(other) == Variable:
			if self.typ in {INT, FLOAT} and other.typ in {INT, FLOAT}:
				return Variable._resolve(self, MINUS, other)
			else: raise Exception('not implemented: -')
		else: # Collection
			mark('cannot subtract collection from variable')
			return other
	def __rsub__(self, other):
		if type(other) == Variable:
			return -self + other
		else: # Collection
			other_copy = deepcopy(other)
			if other_copy.typ != self.typ:	mark('variable and collection primitive type mismatch')
			elif other_copy.const:			mark('arrays cannot be modified')
			else:
				try: 						other_copy.collect.remove(self)
				except ValueError: 			mark('variable not in collection')
				return other_copy
	def __mul__(self, other):
		if type(other) == Variable:
			if other.typ == self.typ or other.typ == {INT,FLOAT} and self.typ in {INT,FLOAT}:
				return Variable._resolve(self,MULT,other)
			else: raise Exception('not implemented: *')
		else: # Collection
			raise Exception('cannot multiply variable by collection')
	def __rmul__(self, other):
		return self * other
	def __truediv__(self, other):
		if type(other) == Variable:
			if other.typ == self.typ or other.typ == {INT,FLOAT} and self.typ in {INT,FLOAT}:
				return Variable._resolve(self,DIV,other)
			else: raise Exception('not implemented: /')
		else: # Collection
			raise Exception('cannot divide variable by collection')
	def __rtruediv__(self, other):
		return Variable._resolve(self,'inv') * other
	def __mod__(self, other):
		if type(other) == Variable:
			if other.typ == self.typ or other.typ == {INT,FLOAT} and self.typ in {INT,FLOAT}:
				return Variable._resolve(self,MOD,other)
			else: raise Exception('not implemented: %')
		else: # Collection
			raise Exception('cannot modulo variable by collection')
	def __rmod__(self, other):
		raise Exception('not implemented: r%')
	def __pow__(self, other):
		if type(other) == Variable:
			if other.typ == self.typ or other.typ == {INT,FLOAT} and self.typ in {INT,FLOAT}:
				return Variable._resolve(self,EXP,other)
			else: raise Exception('not implemented: ^')
		else: # Collection
			raise Exception('cannot exponentiate variable by collection')
	def __rpow__(self, other):
		raise Exception('not implemented: r^')
	def __and__(self, other):
		if type(other) == Variable:
			if other.typ == self.typ == BOOL:
				return Variable._resolve(self,AND,other)
			else: raise Exception('not implemented: &')
		else: # Collection -> works as 'in'
			if self.value in other.collect:	return Variable(BOOL,True)
			else:							return Variable(BOOL,False)
	def __rand__(self, other):
		return self and other
	def __or__(self, other):
		if type(other) == Variable:
			if other.typ == self.typ == BOOL:
				return Variable._resolve(self,OR,other)
			else: raise Exception('not implemented for types')
		else: # Collection
			raise Exception('cannot use conjunction on variable and collection')
	def __ror__(self, other):
		return self or other
	def __eq__(self, other):
		if type(other) == Variable:
			return Variable._resolve(self,EQ,other)
		else: # Collection
			return Variable(BOOL,False)
	def __ne__(self, other):
		if type(other) == Variable:
			return Variable._resolve(self,NE,other)
		else: # Collection
			return Variable(BOOL,True)
	def __lt__(self, other):
		if type(other) == Variable:
			if other.typ == self.typ or other.typ == {INT,FLOAT} and self.typ in {INT,FLOAT}:
				return Variable._resolve(self,LT,other)
			elif other.typ == self.typ == STRING:
				return Variable._resolve(self,LT,other)
			else: raise Exception('not implemented for types')
		else: # Collection
			raise Exception('cannot use order comparison on variable and collection')
	def __gt__(self, other):
		if type(other) == Variable:
			if other.typ == self.typ or other.typ == {INT,FLOAT} and self.typ in {INT,FLOAT}:
				return Variable._resolve(self,GT,other)
			elif other.typ == self.typ == STRING:
				return Variable._resolve(self,GT,other)
			else: raise Exception('not implemented for types')
		else: # Collection
			raise Exception('cannot use order comparison on variable and collection')

	@staticmethod
	def _conv(typ,value):
		# Converts given primative value to the specified type
		if typ == INT:
			return int(value)
		elif typ == FLOAT:
			return float(value)
		elif typ == STRING:
			return str(value)
		elif typ == BOOL:
			return bool(value)
		elif typ == NULL:
			return None
		mark('invalid conversion')

	@staticmethod
	def _resolve(first, op, second = None):
		if op == PLUS: 			val = first.value + second.value
		elif op == MINUS:
			if second == None:	val = -first.value
			else: 				val = first.value - second.value
		elif op == MULT: 		val = first.value * second.value
		elif op == DIV: 		val = first.value / second.value
		elif op == MOD: 		val = first.value % second.value
		elif op == EXP: 		val = first.value ** second.value
		elif op == AND: 		val = first.value and second.value
		elif op == OR: 			val = first.value or second.value
		elif op == EQ: 			val = first.value == second.value
		elif op == NE: 			val = first.value != second.value
		elif op == LT: 			val = first.value < second.value
		elif op == GT: 			val = first.value > second.value

		elif op == 'inv': 		val = 1 / first.value
		else: mark('unknown operator'); val = None

		if type(val) == int: typ = INT
		elif type(val) == float: typ = FLOAT
		elif type(val) == str: typ = STRING
		elif type(val) == bool: typ = BOOL
		elif type(val) == None: typ = NULL
		else: mark('unknown type'); typ = NULL

		return Variable(typ,val)

class Collection:
	def __init__(self, typ, inputs, const = False):
		self.collect = []
		if typ not in PRIMATIVE - {NULL}:
			mark('invalid collection type') # Collections cannot hold null
			self.typ, self.const = NULL, True
		elif type(inputs) != list:
			mark('collection requires list input')
			self.typ, self.const = NULL, True
		else:
			if const not in COLLECTION: self.const = False
			elif const == ARRAY:        self.const = True
			else:                       self.const = False # LIST
			self.typ = typ

			for elem in inputs:
				if type(elem) != Variable or elem.typ != self.typ:
					mark('collection element type mismatch')
				else:
					self.collect.append(elem)

	def __getitem__(self, index):
		# Get numerical value of index
		if type(index) == Variable:
			index = Collection._convIndex(index)

		if index >= len(self.collect):
			mark('invalid index')
			return Variable(NULL,None)
		return self.collect[index]
	def __setitem__(self, index, value):
		if type(index) == Variable:
			index = Collection._convIndex(index)

		if self.const:                      mark('arrays are non-mofifiable')
		else:
			if index >= len(self.collect):  mark('assignment is out of range')
			else:                           self.collect[index].value = value
	def __delitem__(self, index):
		if type(index) == Variable:
			index = Collection._convIndex(index)

		if self.const:                      mark('arrays are non-mofifiable')
		else:
			if index >= len(self.collect):  mark('assignment is out of range')
			else:                           del self.collect[index]
	def __len__(self):
		return len(self.collect)
	def __iter__(self):
		self.__i = 0
		return self
	def __next__(self):
		if self.__i >= len(self.collect):
			raise StopIteration
		else:
			result = self.collect[self.__i]
			self.__i += 1
			return result

	def __int__(self):
		mark('collection cannot be converted to int')
		return Variable(INT,0)
	def __float__(self):
		mark('collection cannot be converted to float')
		return Variable(FLOAT,0)
	def __str__(self):
		toRet = '['
		if len(self.collect)>=1:
			toRet += str(self.collect[0].value)
			for elem in self.collect[1:]:
				toRet += ',' + str(elem.value)
		return toRet + ']'
	def __bool__(self):
		return Variable(BOOL,len(self.collect)>0)

	def __add__(self, other):
		self_copy = deepcopy(self)
		if type(other) == Variable:
			if self_copy.typ != other.typ:	mark('variable and collection mismatch')
			elif self_copy.const: 			mark('cannot modify array')
			else:                       	self_copy.collect.append(other)
		else: # Collection
			for elem in other:
				self_copy = self_copy + elem
				# if self_copy.typ != elem.typ:	mark('variable and collection mismatch')
				# elif self_copy.const: 			mark('cannot modify array')
				# else:
				# 	for elem in other:			self_copy.collect.append(elem)
		return self_copy
	def __sub__(self, other):
		self_copy = deepcopy(self)
		if type(other) == Variable:
			if self_copy.typ != other.typ:  mark('variable and collection mismatch')
			elif self_copy.const: 			mark('cannot modify array')
			else:
				try:                		self_copy.collect.remove(other)
				except ValueError:  		mark('variable not in collection')
		else: # Collection
			for elem in other:
				self_copy = self_copy - elem
				# if self.typ != elem.typ:    mark('variable and collection mismatch')
				# elif self.const: 			mark('cannot modify array')
				# else:
				# 	for elem in other:
				# 		try:                self.collect.remove(other)
				# 		except ValueError:  pass
		return self_copy

SYMBOL = {Variable, Collection}
