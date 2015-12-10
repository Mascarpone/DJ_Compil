# -*- coding: utf-8 -*-
#
# See DJ_compil.py for full description

import sys


class Type:
    '''A generic class to decribe types'''
    def isValue(self):
        return False

    def isFunction(self):
        return False

    def isArray(self):
        return False


class ValueType(Type):
    '''A generic class to decribe types'''
    def __init__(self):
        self.t = None

    def isValue(self):
        return True

    def setVoid():
        self.t = "void"

    def isVoid():
        return self.t = "void"

    def setInt(self):
        self.t = "i32"

    def isInt(self):
        return self.t == "i32"

    def setChar(self):
        self.t = "i8"

    def isChar(self):
        return self.t == "i8"

    def setFloat(self):
        self.t = "float"

    def isFloat(self):
        return self.t == "float"

    def setUndefined(self):
        self.t = None

    def isUndefined(self):
        return self.t == None


class FunctionType(Type):
    '''A generic class to decribe types'''
    def __init__(self):
        self.r = None
        self.a = [] # list

    def isFunction(self):
        return True

    def setReturnType(t):
        self.r = t

    def getReturnType():
        return self.r

    def setArgType(i, t):
        if i < len(self.a):
            self.a[i] = t
        elif i == len(self.a):
            self.a.append(t)
        else:
            raise IndexError

    def getArgType(i):
        return self.a[i]


class ArrayType(Type):
    '''A generic class to decribe types'''
    def isArray(self):
        return True









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
        self.id_type[id] = t

    def getAddr(self, id):
        '''returns the string corresponding to the register in which this adress returned for this id by alloca is stored'''
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
        else:
            self.id_type = self.prev.id_type
            self.id_addr = self.prev.id_addr
            self.prev = self.prev.prev



# Types checking
def getType(t1, t2, l):
    '''returns the type of the return value of a two-variable operation (*, +, /, -)
       the types in the checkTable are in order : "INT", "FLOAT", "CHAR", None'''
    checkTable = {}
    checkTable["i32"] = {"i32" : "i32", "float" : "float", "i8" : "i32", None : None}
    checkTable["float"] = {"i32" : "float", "float" : "float", "i8" : "float", None : None}
    checkTable["i8"] = {"i32" : "i32", "float" : "float", "i8" : "i8", None : None}
    checkTable[None] = {"i32" : None, "float" : None, "i8" : None, None : None}
    if t1[0] != "v" or t2[0] != "v" or checkTable[t1[1]][t2[1]] is None:
        sys.stderr.write("*ERROR* Incompatible types in operation on line " + str(l) + "\n")
        raise SyntaxError
    return ["v", checkTable[t1[1]][t2[1]]]

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


# A type is a list
# the first element tells if it's a simple value (i32, float, i8), an array, or a function
#   - "v" : simple value
#   - "a" : array
#   - "f" : function
# the second element is the type of the element
#   - if it's a value the type is a string representing the type
#   - if it's a 1D array, the type is a string representing the type of the elements, if it's a 2D+ array, it's a new list describing the sub-array
#   - if it's a function, the type is a function with first element as return type, and others elements as arguments.



def warning(lineno, msg):
    sys.stderr.write("*WARNING* (l." + str(lineno) + "): " + msg + "\n")


def error(lineno, msg):
    #global produce_code
    #produce_code = False
    sys.stderr.write("*ERROR* (l." + str(lineno) + "): " + msg + "\n")
    raise SyntaxError




def checkGenericErrors(cc, result):
    '''Check result to throw errors/warnings at the end of the compilation'''
    # look for main
    if result is None:
        return
    if not cc.exists("main"):
        sys.stderr.write("*WARNING* this program doesn't have a main() function\n")
