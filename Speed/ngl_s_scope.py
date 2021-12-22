# NGL Speed Scope Class

import ngl_s_ast2 as AST
from ngl_s_sc import mark
from typing import Dict, List, Union

# The scope class is used to track currently established and assigned variables during parsing.
class SymbolTable:
	def __init__(self):
		self._scopes: List[Dict[str, AST.DataType]] = [] # Var name to data type
		self._funcs: List[Dict[str, AST.DataType]] = [] # Func name to return type

		self.newScope()

	def newScope(self):
		self._scopes.append({})
		# print(f'N{self.size()-1}, {self._scopes}')

	def popScope(self):
		if (len(self._scopes) > 1):
			# print(f'P{self.size()-1}, {self._scopes}')
			self._scopes.pop()
		else:
			mark('cannot remove last scope')

	def search(self, var: str, burrow = True) -> Union[AST.DataType, None]:
		if var in self.top():
			return self.top()[var]
		elif burrow:
			for i in range(self.size()-1, 0, -1):
				if var in self._select(i):
					return self._select(i)[var]
		return None

	def search_function(self, var: str) -> Union[AST.DataType, None]:
		if var in self._funcs:
			return self._funcs[var]
		return None

	def assign(self, var: str, val: AST.DataType, burrow=True) -> None:
		if var in self.top():
			self.top()[var] = val
		elif burrow:
			for i in range(self.size()-1, 0, -1):
				if var in self._select(i):
					self._select(i)[var] = val
					return
			self.top()[var] = val

	def assign_function(self, var: str, val: AST.DataType) -> None:
		self._funcs[var] = val

	def delete(self, var: str) -> None:
		if var in self.top():
			del self.top()[var]

	def top(self):
		return self._select(-1)

	def _select(self, scope: int):
		return self._scopes[scope]

	def size(self):
		return len(self._scopes)

	def __repr__(self):
		return str(self._scopes)
