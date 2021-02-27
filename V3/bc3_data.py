# NGL Bytecode 3.0 Data Containers

# Simple Types

class Value:
    def __init__(self,const=False):
        self.const = const
    def __eq__(self,other):
        return type(self) == type(other) or type(other) == Ref

class Int(Value):
    # Represents an integer
    def __str__(self):
        return 'int'

class Float(Value):
    # Represents a floating point number
    def __str__(self):
        return 'float'

class Str(Value):
    # Represents a string
    def __str__(self):
        return 'str'

class Bool(Value):
    # Represents a boolean
    def __str__(self):
        return 'bool'

class Func(Value):
    # Represents a function: can be converted to the full runtime version
    def __init__(self,value,const=False):
        super().__init__(const)
        self.val = value # represents file name
    def __str__(self):
        return 'func({0})'.format(self.val)

class Lab(Value):
    # Represents a label: can be converted to the full runtime version
    def __init__(self,value,const=False):
        super().__init__(const)
        self.val = value # represents jump destination
    def __str__(self):
        return 'label({0})'.format(self.val)

class Ref:
    # Represents a variable or function call where the type is not know at compile time
    def __init__(self,typ,data=None):
        self.type = typ
        self.data = data
    def __str__(self):
        return 'ref({0})'.format(self.type)
    def __eq__(self,other):
        if type(other) in set({Int,Float,Str,Bool,Func,Lab}) or type(other) == Ref:
            return True
        return False


# Runtime Types

class Const:
    def __init__(self,typ,val=None):
        self.type = typ
        self.val = val
    def __eq__(self,other):
        if other in SIMPLE:
            return self.type == other.type and self.val == other.val
        return False
    def __str__(self):
        return 'Const {0}::{1}'.format(self.val,self.type)

class Var:
    def __init__(self,typ,val=None):
        self.type = typ
        self.val = val
    def __eq__(self,other):
        if other in SIMPLE:
            return self.type == other.type and self.val == other.val
        return False
    def __str__(self):
        return 'Var {0}::{1}'.format(self.val,self.type)

class Array:
    def __init__(self,typ,val=None):
        self.type = typ
        self.val = val
    def __eq__(self,other):
        if other == None: return False
        return self.type == other.type and self.val == other.val
    def __str__(self):
        return 'Array of {0}::{1}'.format(self.type,self.val) if self.val != None else 'Array of {0}'.format(self.type)

class List:
    def __init__(self,typ,val=None):
        self.type = typ
        self.val = val
    def __eq__(self,other):
        if other == None: return False
        return self.type == other.type and self.val == other.val
    def __str__(self):
        return 'List of {0}::{1}'.format(self.type,self.val) if self.val != None else 'List of {0}'.format(self.type)

class Function:
    # A callable function (must be included)
    #fields: name, filename, param number
    def __init__(self,fname):
        self.val = fname
    def __eq__(self,other):
        if other in COMPLEX:
            return self.type == other.type and self.value == other.value
        return False
    def __str__(self):
        return 'Func in {0}'.format(self.val)

class Label:
    # A representation of a jumpable line
    def __init__(self,value):
        # self.type = name # Label name
        self.val = value # jump destination
    def __eq__(self,other):
        return False
    def __str__(self):
        # return 'Label {0} at {1}'.format(self.type,self.val+1) # add 1 to line up with text editor
        return 'Label at {0}'.format(self.val+1) # add 1 to line up with text editor

class Arrow:
    # A representation of an arrow
    def __init__(self,name,value=-1):
        self.type = name # Label name
        self.val = value # jump destination
    def __eq__(self,other):
        return False
    def __str__(self):
        return 'Arrow {0} from {1}'.format(self.type,self.val)

class Error:
    # A representation of an exception
    pass

CONTAINERS  = set({Const,Var,Array,List})
PRIMITIVES  = set({Int,Float,Str,Bool})
SIMPLE      = set({Const,Var,Label})
COMPLEX     = set({Array,List,Function})
NONDATA     = set({Error})


# (TBD) Non constant value (like from a variable)
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

    def __str__(self):
        if type(self.type) == Float:    typ = 'float'
        elif type(self.type) == Int:    typ = 'int'
        elif type(self.type) == Str:    typ = 'str'
        else:                           typ = 'bool'
        return 'Const {0}::{1}'.format(self.value,typ)


    def __eq__(self,other):
        if type(other) == type(self):
            return self.type == other.type and self.value == other.value
        return False

    def __ne__(self,other):
        return not self == other

# Represents a variable reference (used exclusively within the symbol table)
class VariableValue(Constant):
    def __init__(self, typ, value=None):
        super().__init__(typ,None)
        if value != None:
            self.setValue(value)

    def __str__(self):
        if type(self.type) == Float:    typ = 'float'
        elif type(self.type) == Int:    typ = 'int'
        elif type(self.type) == Str:    typ = 'str'
        else:                           typ = 'bool'
        return 'Var {0}::{1}'.format(self.value,typ)

    def setValue(self,value):
        self.value = value

# Represents a constant collection
class ConstantArray:
    def __init__(self, typ, value):
        self.type = typ
        self.value = tuple(value)

    def __str__(self):
        if type(self.type) == Float:    typ = 'float'
        elif type(self.type) == Int:    typ = 'int'
        elif type(self.type) == Str:    typ = 'str'
        else:                           typ = 'bool'
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
        if self.type == Int:  typ = 'float'
        elif self.type == Int:  typ = 'int'
        elif self.type == Str:  typ = 'str'
        else:                   typ = 'bool'
        return 'List {0}::{1}'.format(self.value,typ)

    def setValue(self,value,index=None):
        if index == None:
            self.value = list(value)
        else:
            self.value[index] = value


if __name__ == '__main__':
    pass
