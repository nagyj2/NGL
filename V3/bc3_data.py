# NGL Bytecode 3.0 Data Containers

from bc3_scanner import INT, FLOAT, STR, BOOL

# (TBD)
# class Value:
#     def __init__(self,typ,value):
#         self.type = typ
#         self.value = value
#
#     def __eq__(self,other):
#         if type(other) == type(self):
#             return self.type == other.type and self.value = other.value
#         return False

class Int:
    def __eq__(self,other):
        return type(self) == type(other)

class Float:
    def __eq__(self,other):
        return type(self) == type(other)

class Str:
    def __eq__(self,other):
        return type(self) == type(other)

class Bool:
    def __eq__(self,other):
        return type(self) == type(other)

class Array:
    def __init__(self,typ):
        self.type = typ
    def __eq__(self,other):
        return type(self) == type(other) and self.type == other.type

class List:
    def __init__(self,typ):
        self.type = typ
    def __eq__(self,other):
        return type(self) == type(other) and self.type == other.type

# Represents a value constant
class ConstantValue:
    def __init__(self, typ, value):
        self.type = typ
        self.value = value

    def __str__(self):
        if self.type == FLOAT:  typ = 'float'
        elif self.type == INT:  typ = 'int'
        elif self.type == STR:  typ = 'str'
        else:                   typ = 'bool'
        return 'Const {0}::{1}'.format(self.value,typ)


    def __eq__(self,other):
        if type(other) == type(self):
            return self.type == other.type and self.value == other.value
        return False

    def __ne__(self,other):
        return not self == other

# Represents a variable value (used exclusively within the symbol table)
class VariableValue(Constant):
    def __init__(self, typ, value=None):
        super().__init__(typ,None)
        if value != None:
            self.setValue(value)

    def __str__(self):
        if self.type == FLOAT:  typ = 'float'
        elif self.type == INT:  typ = 'int'
        elif self.type == STR:  typ = 'str'
        else:                   typ = 'bool'
        return 'Var {0}::{1}'.format(self.value,typ)

    def setValue(self,value):
        self.value = value

# Represents a constant collection
class ConstantArray:
    def __init__(self, typ, value):
        self.type = typ
        self.value = tuple(value)

    def __str__(self):
        if self.type == FLOAT:  typ = 'float'
        elif self.type == INT:  typ = 'int'
        elif self.type == STR:  typ = 'str'
        else:                   typ = 'bool'
        return 'Array {0}::{1}'.format(self.value,typ)

    @property
    def len(self):
        return len(self.value)

    def __eq__(self,other):
        if type(other) == type(self) and self.type == other.type and len(self.value) == len(other.value):
            for i in range(len(self.value)):
                if self.value[i] != other.value[i]: return False
            return True
        return False

    def __ne__(self,other):
        return not self == other

# Represents a variable collection (used exclusively within the symbol table)
class VariableArray(Array):
    def __init__(self, typ, value):
        super().__init__(typ,value)
        self.value = list(self.value)

    def __str__(self):
        if self.type == FLOAT:  typ = 'float'
        elif self.type == INT:  typ = 'int'
        elif self.type == STR:  typ = 'str'
        else:                   typ = 'bool'
        return 'List {0}::{1}'.format(self.value,typ)

    def setValue(self,value,index=None):
        if index == None:
            self.value = list(value)
        else:
            self.value[index] = value

# A callable function (must be included)
class Function:
    #fields: name, filename, param number
    pass

# A representation of a jumpable line
class Label:
    #fields: name, filename, param number
    pass

# A representation of an exception
class Error:
    pass

if __name__ == '__main__':
    pass
