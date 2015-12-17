# -*- coding: utf-8 -*-
#
# See DJ_compil.py for full description

import sys


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def warning(lineno, msg):
    sys.stderr.write(bcolors.WARNING + "*WARNING*" + bcolors.ENDC + " (l." + str(lineno) + "): " + msg + "\n")


def error(lineno, msg):
    #global produce_code
    #produce_code = False
    sys.stderr.write(bcolors.FAIL + "*ERROR*" + bcolors.ENDC + " (l." + str(lineno) + "): " + msg + "\n")
    raise SyntaxError


def internal_error(lineno, msg):
    #global produce_code
    #produce_code = False
    sys.stderr.write(bcolors.FAIL + "*INTERNAL ERROR*" + bcolors.ENDC + " (l." + str(lineno) + "): " + msg + "\n")
    raise SystemError



class Type:
    '''A generic class to decribe types'''
    def isValue(self):
        return False

    def isArray(self):
        return False

    def isFunction(self):
        return False

    def getOpResultType(self, arg2):
        '''returns the type of the return value of a two-variable operation (*, +, /, -)
        between self and arg2.'''
        return None # because it is not generally defined

    def equals(t2):
        return False


class ValueType(Type):
    '''A class to decribe primary types'''
    def __init__(self, t = -1):
        self.t = t

    def isValue(self):
        return True

    def isDefined(self):
        return self.t != -1

    def equals(t2):
        if t2.isValue():
            return self.t == t2.t
        else:
            return False

    def __str__(self):
        '''returns IR of type'''
        try:
            return ["void","i32","i8","float"][self.t]
        except IndexError:
            raise TypeError # type is None or undefined

    def getOpResultType(self, arg2):
        '''returns the type of the return value of a two-variable operation (*, +, /, -)
        between self and arg2.'''
        if not arg2.isValue():
            return None
        else:
            checkTable = [
            # void, int,  char, float
            [0,     0,    0,    0], # 0=void
            [0,     1,    1,    3], # 1=int
            [0,     1,    2,    3], # 2=char
            [0,     3,    3,    3]  # 3=float
            ]
            return ValueType(checkTable[self.t][arg2.t])


ValueType.VOID  = ValueType(0)
ValueType.INT   = ValueType(1)
ValueType.CHAR  = ValueType(2)
ValueType.FLOAT = ValueType(3)


class FunctionType(Type):
    '''A class to decribe function types'''
    def __init__(self, ret = ValueType.VOID, args = []):
        self.r = ret
        self.a = args # list

    def isFunction(self):
        return True

    def setReturnType(self, t):
        self.r = t

    def getReturnType(self):
        return self.r

    def getArgsCount():
        return len(self.a)

    def setArgType(self, i, t):
        if 0 <= i and i < len(self.a):
            self.a[i] = t
        elif i == len(self.a):
            self.a.append(t)
        else:
            raise IndexError

    def getArgType(self, i):
        return self.a[i]

    def equals(t2):
        if t2.isFunction():
            if not self.getReturnType().equals(t2.getReturnType()):
                return False
            if self.getArgsCount() != t2.getArgsCount():
                return False
            for arg_t1, arg_t2 in zip(self.a, t2.a):
                if not arg_t1.equals(arg_t2):
                    return False
            return True
        else:
            return False

    def __str__(self):
        return self.r + "(" + ", ".join(self.a) + ")*"


class ArrayType(Type):
    '''A generic class to decribe types'''
    def __init__(self, elt):
        self.elt = elt

    def isArray(self):
        return True

    def setElementsType(self, t):
        self.elt = t

    def getElementsType(self):
        return self.elt

    def equals(t2):
        if t2.isArray():
            return self.elt.equals(t2.elt)
        else:
            return False

    def __str__(self):
        global cc
        return cc.array_types[str(self.elt)]




# ids and their corresponding types
class Context:
    '''A class to describe ids visibility and their corresponding types'''

    # the surrounding context. If it's None, it means that it's the global context
    prev = None
    # the dictionary associating each id to its type
    id_type = {}
    # dictionary for adresses of allocated IDs
    id_addr = {}

    def __init__(self, c = None):
        '''Creates a new context, with c as surrounding context'''
        self.prev = c
        self.id_type = {}
        self.id_addr = {}
        self.glob = self if c is None else c.glob
        self.array_types = {}
        self.array_types_counter = 0

    def getParent(self):
        '''returns the surrounding context'''
        return self.prev

    def getGlobalContext(self):
        '''returns the global context'''
        return self.glob

    def isGlobal(self):
        '''Tells if this context is the global context (no parent)'''
        return self.prev is None

    def exists(self, id):
        '''tells if an id is known in the current context'''
        if id in self.id_type:
            return True
        elif self.prev is None:
            return False
        else:
            return self.prev.exists(id)

    def getType(self, id):
        '''returns the type of an id, or None if not reachable in current context'''
        if id in self.id_type:
            return self.id_type[id]
        elif self.prev is None:
            return None
        else:
            return self.prev.getType(id)

    def setType(self, id, t):
        '''sets the type of id in current context to t'''
        if t.isArray():
            if not str(t) in self.array_types:
                self.array_types[str(t.elt)] = "%array" + str(self.array_types_counter)
                self.array_types_counter += 1
        self.id_type[id] = t

    def getAddr(self, id):
        '''returns the string corresponding to the register in which the adress returned for this id by alloca is stored'''
        if id in self.id_addr:
            return self.id_addr[id]
        elif self.prev is None:
            return None
        else:
            return self.prev.getAddr(id)

    def setAddr(self, id, a):
        '''sets the register in which id is allocated to a'''
        self.id_addr[id] = a

    def new(self):
        '''Sets current context as a new context with the previous surrounding context as parent.
        e.g. when entering a { ... } block'''
        nc = Context()
        nc.prev = self.prev
        nc.id_type = self.id_type
        nc.addr = self.id_addr
        self.prev = nc
        self.id_type = {}
        self.id_addr = {}

    def close(self):
        '''Set current context back to its parent'''
        if self.isGlobal():
            # is there a best way to raise an error ?
            sys.stderr.write("*ERROR*: trying to close global context\n")
            # raise ... ?
        else:
            self.id_type = self.prev.id_type
            self.id_addr = self.prev.id_addr
            self.prev = self.prev.prev


# A type is a list
# the first element tells if it's a simple value (i32, float, i8), an array, or a function
#   - "v" : simple value
#   - "a" : array
#   - "f" : function
# the second element is the type of the element
#   - if it's a value the type is a string representing the type
#   - if it's a 1D array, the type is a string representing the type of the elements, if it's a 2D+ array, it's a new list describing the sub-array
#   - if it's a function, the type is a function with first element as return type, and others elements as arguments.


def type2str(t):
    '''prints the type t as a string in dj coding convention'''
    if t[0] == "v":
        d = {"i32" : "int", "i8" : "char", "float" : "float", "void" : "void"}
        return d[t[1]]
    elif t[0] == "a":
        return type2str(t[1]) + "[]"
    elif t[0] == "f":
        if len(t[1]) > 1:
            return type2str(t[1][0]) + "(*)(" + ", ".join(map(type2str, t[1][1:])) + ")"
        else:
            return type2str(t[1][0]) + "(*)()"


#def isValue(t):
#    '''tells if t is a value type'''
#    return t[0] == "v"
#
#def isArray(t):
#    '''tells if t is an array type'''
#    return t[0] == "a"
#
#def isFunction(t):
#    '''tells if t is a function type'''
#    return t[0] == "f"


def generateArrayType(context):
    '''returns the code defining the array types'''
    code = ""
    for elt_type, type_name in context.array_types.items():
        code += type_name + " = type { i32, " + elt_type + " }\n"


# Label generation
LAB_NB = 0
def newLab():
    global LAB_NB
    LAB_NB += 1
    return "label" + str(LAB_NB)

# Registre generation
RG_NB = 0
def newReg():
    global RG_NB
    RG_NB += 1
    return "%r" + str(RG_NB)

# Global variable generation
GB_NB = 0
def newGBVar():
    global GB_NB
    GB_NB += 1
    return "@.var" + str(GB_NB)

# Converts float to hex
import struct
def float_to_hex(value):
    v = struct.unpack('f', struct.pack('f', value))[0]
    raw = struct.pack('d', float(v))
    intrep = struct.unpack('Q', raw)[0]
    out = '{{0:#{0}x}}'.format(16).format(intrep)
    return out


def checkGenericErrors(cc, result):
    '''Check result to throw errors/warnings at the end of the compilation'''
    # look for main
    if result is None: # check if compilation reached the end
        return
    if not cc.exists("main"):
        sys.stderr.write("*WARNING* this program doesn't have a main() function\n")
