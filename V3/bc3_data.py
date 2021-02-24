# NGL Bytecode 3.0 Data Containers

import logging

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

# Represents a value constant
class Constant:
    def __init__(self, typ, value):
        self.type = typ
        self.value = value

    def __eq__(self,other):
        if type(other) == type(self):
            return self.type == other.type and self.value == other.value
        return False

    def __ne__(self,other):
        return not self == other


# Represents a variable value (used exclusively within the symbol table)
class Variable(Constant):
    def __init__(self, typ, value=None):
        super().__init__(typ,None)
        if value != None:
            self.setValue(value)

    def setValue(self,value):
        self.value = value

# Represents a constant collection
class Array:
    def __init__(self, typ, value):
        self.type = typ
        self.value = tuple(value)

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
class List(Array):
    def __init__(self, typ, value):
        super().__init__(typ,value)
        self.value = list(self.value)

    def setValue(self,value,index=None):
        if index == None:
            self.value = list(value)
        else:
            self.value[index] = value

# A callable function (must be included)
class Function:
    pass

if __name__ == '__main__':
    pass
