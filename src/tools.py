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

    def equals(self, t2):
        return False


class ValueType(Type):
    '''A class to decribe primary types'''
    def __init__(self, t = -1):
        self.t = t

    def isValue(self):
        return True

    def isDefined(self):
        return self.t != -1

    def equals(self, t2):
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

    def getArgsCount(self):
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

    def equals(self, t2):
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

    def equals(self, t2):
        if t2.isArray():
            return self.elt.equals(t2.elt)
        else:
            return False

    def __str__(self):
        return "{ i32, " + str(self.elt) + "* }"


def type2str(t):
    '''prints the type t as a string in dj coding convention'''
    if t.isValue():
        return ["void", "int", "char", "float"][t.t]
    elif t.isArray():
        return type2str(t.getElementsType()) + "[]"
    elif t.isFunction():
        if len(t.getArgsCount()) > 0:
            return type2str(t.getReturnType()) + "(" + ", ".join(map(type2str, t.a)) + ")"
        else:
            return type2str(t.getReturnType()) + "()"



# ids and their corresponding types
class Context:
    '''A class to describe ids visibility and their corresponding types'''

    def __init__(self, c = None):
        '''Creates a new context, with c as surrounding context'''
        self.prev = c                               # surrounding context
        self.id_type = {}                           # store the type of declared variables. key = var name, value = Type instance
        self.id_addr = {}                           # store the allocated adress of variables. key = var name, value = reg containing addr
        self.glob = self if c is None else c.glob   # remember global context if needed. ** UNUSED ** delete it ?
        self.compound_statement_open_new_cc = True  # set it to False to prevent compound_statement from opening a new cc
        self.return_types_found = []                # used to check if returned values have a good type
        self.text = {}                              # strings that will be definded as global variables. key = string, value = global name
        self.text_counter = 0                       # a counter to name strings
        self.map_functions = {}                     # used to generate map functions for each type of parameters
        self.map_functions_counter = 0              # counter for map functions
        self.reduce_functions = {}                  # used to generate reduce functions for each type of parameters
        self.reduce_functions_counter = 0           # counter for reduce functions


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

    def unactivateOpenNewContext(self):
        '''Sets compound_statement_open_new_cc to false to prevent compound_statement from opening a new context'''
        self.compound_statement_open_new_cc = False

    def activateOpenNewContext(self):
        '''Sets compound_statement_open_new_cc to true to allow compound_statement to open a new context'''
        self.compound_statement_open_new_cc = True

    def compoundStatementOpenNewContext(self):
        '''returns compound_statement_open_new_cc'''
        return self.compound_statement_open_new_cc

    def addReturnType(self, t):
        '''sets return_types_found to check return types'''
        self.return_types_found.append(t)

    def getReturnTypes(self):
        '''returns return_types_found'''
        return self.return_types_found

    def resetReturnTypes(self):
        '''reset the list of return types found to []'''
        self.return_types_found = []

    def new(self):
        '''Sets current context as a new context with the previous surrounding context as parent.
        e.g. when entering a { ... } block'''
        nc = Context()
        nc.prev = self.prev
        nc.id_type = self.id_type
        nc.id_addr = self.id_addr
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

    def addText(self, lineno, text):
        '''adds a new constant string'''
        if not text in self.text:
            esc_str, l = escape_string(lineno, text)
            self.text[text] = ("@str." + str(self.text_counter), esc_str, l)
            self.text_counter += 1
        return self.text[text]

    def generateText(self):
        '''returns the code defining the constant strings'''
        code = ""
        for var_name, esc_str, l in self.text.values():
            code += var_name + " = internal constant [" + str(l) + " x i8] c\"" + esc_str + "\"\n"
        return code

    def getMapFunction(self, type_in, type_out):
        '''returns the name of the map function which apply a function with prototype "type_out(type_in)"'''
        key = (str(type_in), str(type_out))
        if not key in self.map_functions:
            self.map_functions[key] = ("@map." + str(self.map_functions_counter), type_in, type_out)
        return self.map_functions[key][0]

    def generateMapFunctions(self):
        code = ""
        for name, type_in, type_out in self.map_functions.values():
            ti = ArrayType(type_in)
            to = ArrayType(type_out)
            fct_t = FunctionType(to, [ti])
            code += "define " + str(to) + " " + name + "(" + str(fct_t) + " %f, " + str(ti) + " %t) {\n"
            code += "; ... \n"
            code += "}\n"
        return code

    def getReduceFunction(self, t):
        '''returns the name of the reduce function which apply a function with prototype "t(t,t)"'''
        key = str(t)
        if not key in self.reduce_functions:
            self.reduce_functions[key] = ("@reduce." + str(self.reduce_functions_counter), t)
        return self.reduce_functions[key][0]

    def generateReduceFunctions(self):
        code = ""
        for name, t in self.reduce_functions.values():
            te = ArrayType(t)
            fct_t = FunctionType(te, [te, te])
            code += "define " + str(te) + " " + name + "(" + str(fct_t) + " %f, " + str(ti) + " %t) {\n"
            code += "; ... \n"
            code += "\n"
        return code


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
    return "@gbvar" + str(GB_NB)


def sizeof(t):
    '''return the size of an element of type t'''
    if t.isArray() or t.isFunction(): # it's a pointer
        return 8
    elif t.isValue():
        return [None, 4, 1, 4][t.t]


# Converts float to hex
import struct
def float_to_hex(value):
    v = struct.unpack('f', struct.pack('f', value))[0]
    raw = struct.pack('d', float(v))
    intrep = struct.unpack('Q', raw)[0]
    out = '{{0:#{0}x}}'.format(16).format(intrep)
    return out


def escape_string(lineno, s):
    '''returns the string s with escaped or non-pritable characters replaced by ASCII code'''
    if sys.version_info[0] >= 3: # escape string, depending on python version
        s2 = bytes(s[1:-1], "utf-8").decode("unicode_escape")
    else:
        s2 = s[1:-1].decode('string_escape')
    p = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ!\"#$%&'()*+,-./:;<=>?@[\]^_`{|}~ " #string.printable[:-5] # all printable chars except \n \t \r ...
    r = []
    l = len(s2)
    for i in range(len(s2)):
        if ord(s2[i]) >= 128: # not ascii
            error(lineno, "The character no " + str(i) + " of the string is not ASCII.")
        elif s2[i] in p:
            r.append(s2[i])
        else:
            c = hex(ord(s2[i]))[2:]
            r.append("\\" + "0" * (2 - len(c)) + c.upper())
    return ("".join(r), l)


def checkGenericErrors(cc, result):
    '''Check result to throw errors/warnings at the end of the compilation'''
    # look for main
    if result is None: # check if compilation reached the end
        return
    if not cc.exists("main"):
        sys.stderr.write("*WARNING* this program doesn't have a main() function\n")
