# -*- coding: utf-8 -*-
#
# See DJ_compil.py for full description

import sys, platform


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
    exit(1)


def internal_error(lineno, msg):
    #global produce_code
    #produce_code = False
    sys.stderr.write(bcolors.FAIL + "*INTERNAL ERROR*" + bcolors.ENDC + " (l." + str(lineno) + "): " + msg + "\n")
    exit(2)



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
        return (str(self.r) + "(" + ", ".join(map(str,self.a)) + ")*")


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

# Label generation
LAB_NB = 0
def newLab():
    global LAB_NB
    LAB_NB += 1
    return "label" + str(LAB_NB)


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
        self.let_compound_statement_manage = []     # when compound_statement opens a new context, ir remember it here with a bool to close it
        self.return_types_found = []                # used to check if returned values have a good type
        self.text = {}                              # strings that will be definded as global variables. key = string, value = global name
        self.text_counter = 0                       # a counter to name strings
        self.map_functions = {}                     # used to generate map functions for each type of parameters
        self.map_functions_counter = 0              # counter for map functions
        self.reduce_functions = {}                  # used to generate reduce functions for each type of parameters
        self.reduce_functions_counter = 0           # counter for reduce functions
        self.break_labels = []                      # list of exit labels for loops
        self.continue_labels = []                   # list of next loop labels for loops


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
# begin of deprecated
    def unactivateOpenNewContext(self):
        '''Sets compound_statement_open_new_cc to false to prevent compound_statement from opening a new context'''
        self.compound_statement_open_new_cc = False

    def activateOpenNewContext(self):
        '''Sets compound_statement_open_new_cc to true to allow compound_statement to open a new context'''
        self.compound_statement_open_new_cc = True

    def compoundStatementOpenNewContext(self):
        '''returns compound_statement_open_new_cc'''
        return self.compound_statement_open_new_cc
# end of deprecated
    def claimCCManagement(self):
        '''Sets opening of CC to manual for the next compound statement opening'''
        self.compound_statement_open_new_cc = False

    def giveBackCCManagement(self):
        self.compound_statement_open_new_cc = True

    def pushCCManagementClaim(self):
        '''Push current status of CC management in list for memory, set it back to automatic, and returns the status before reset'''
        self.let_compound_statement_manage.append(self.compound_statement_open_new_cc)
        r = self.compound_statement_open_new_cc
        self.compound_statement_open_new_cc = True
        return r

    def popCCManagementClaim(self):
        return self.let_compound_statement_manage.pop()

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
            internal_error("trying to close global context\n")
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

    def getLastBreakLabel(self):
        '''Returns the label to the end of the last loop we entered or None if there is no loop'''
        if len(self.break_labels) > 0:
            return self.break_labels[-1]
        else:
            return None

    def getLastContinueLabel(self):
        '''Returns the label to the next iteration of the last loop we entered or None if there is no loop'''
        if len(self.continue_labels) > 0:
            return self.continue_labels[-1]
        else:
            return None

    def enterLoop(self):
        '''Creates two labels for the loop we are entering. One for break and one for continue'''
        b = newLab()
        c = newLab()
        self.break_labels.append(b)
        self.continue_labels.append(c)
        return b, c

    def exitLoop(self):
        '''Removes the labels of the last loop we entered when we exit it'''
        if len(self.break_labels) > 0:
            self.break_labels.pop()
        else:
            internal_error(0, "Trying to close a non-existing loop. (break)")
        if len(self.continue_labels) > 0:
            self.continue_labels.pop()
        else:
            internal_error(0, "Trying to close a non-existing loop. (continue)")

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
            fct_t = FunctionType(type_out, [type_in])
            code += "define " + str(to) + " " + name + "(" + str(fct_t) + " %f, " + str(ti) + " %a) {\n"
            code += "  %i = alloca i32\n"
            code += "  store i32 0, i32* %i\n"
            code += "  %size = extractvalue "+ str(ti) + " %a, 0\n"
            if type_out.equals(ValueType.VOID):
                pass
            else:
                code += "  %ret = alloca " + str(to) + "\n"
                code += "  %ret.size.ptr = getelementptr " + str(to) + "* %ret, i32 0, i32 0\n"
                code += "  store i32 %size, i32* %ret.size.ptr\n"
                code += "  %may.not.allocate = icmp eq i32 %size, 0\n"
                code += "  br i1 %may.not.allocate, label %loopmap_exit, label %allocation\n\n"

                code += "  allocation:\n"
                code += "  %buff.bytesize.i32 = mul i32 %size, " + str(sizeof(type_out)) + "\n"
                code += "  %buff.bytesize.i64 = sext i32 %buff.bytesize.i32 to i64\n"
                code += "  %buff.i8 = call i8* @malloc(i64 %buff.bytesize.i64)\n"
                code += "  %buff.tyout = bitcast i8* %buff.i8 to " + str(type_out) + "*\n"
                code += "  %ret.buff.ptr = getelementptr " + str(to) + "* %ret, i32 0, i32 1\n"
                code += "  store " + str(type_out) + "* %buff.tyout, " + str(type_out) + "** %ret.buff.ptr\n"
                code += "  %ret.buff = load " + str(type_out) + "** %ret.buff.ptr\n"
            code += "  %a.buff = extractvalue " + str(ti) + " %a, 1\n"
            code += "  br label %loopmap_head\n\n"

            code += "loopmap_head:\n"
            code += "  %index = load i32* %i\n"
            code += "  %again = icmp slt i32 %index, %size\n"
            code += "  br i1 %again, label %loopmap_body, label %loopmap_exit\n\n"

            code += "loopmap_body:\n"
            code += "  %elt.ptr = getelementptr " + str(type_in) + "* %a.buff, i32 %index\n"
            code += "  %elt = load " + str(type_in) + "* %elt.ptr\n"
            if type_out.equals(ValueType.VOID):
                code += "  call void %f(" + str(type_in) + " %elt)\n"
            else:
                code += "  %res.fct = call " + str(type_out) + " %f(" + str(type_in) + " %elt)\n"
                code += "  %ret.elt.ptr = getelementptr " + str(type_out) + "* %ret.buff, i32 %index\n"
                code += "  store " + str(type_out) + " %res.fct, " + str(type_out) + "* %ret.elt.ptr\n"
            code += "  br label %loopmap_close\n\n"

            code += "loopmap_close:\n"
            code += "  %index.next = add i32 %index, 1\n"
            code += "  store i32 %index.next, i32* %i\n"
            code += "  br label %loopmap_head\n\n"

            code += "loopmap_exit:\n"
            if type_out.equals(ValueType.VOID):
                code += "  ret void\n"
            else:
                code += "  %ret.struct = load " + str(to) + "* %ret\n"
                code += "  ret " + str(to) + "%ret.struct\n"
            code += "}\n\n"
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
            fct_t = FunctionType(t, [t, t])
            code += "define " + str(t) + " " + name + "(" + str(fct_t) + " %f, " + str(te) + " %a) {\n"
            code += "  %size = extractvalue "+ str(te) + " %a, 0\n"
            code += "  %buff = extractvalue " + str(te) + " %a, 1\n"
            code += "  %ret = alloca " + str(t) + "\n"
            code += "  %isempty = icmp eq i32 %size, 0\n"
            code += "  br i1 %isempty, label %loopreduce_exit, label %readfirst\n\n"

            code += "readfirst:\n"
            code += "  %first.ptr = getelementptr " + str(t) + "* %buff, i32 0\n"
            code += "  %first = load " + str(t) + "* %first.ptr\n"
            code += "  store " + str(t) + " %first, " + str(t) + "* %ret\n"

            code += "  %i = alloca i32\n"
            code += "  store i32 1, i32* %i\n"
            code += "  br label %loopreduce_head\n\n"

            code += "loopreduce_head:\n"
            code += "  %index = load i32* %i\n"
            code += "  %again = icmp slt i32 %index, %size\n"
            code += "  br i1 %again, label %loopreduce_body, label %loopreduce_exit\n\n"

            code += "loopreduce_body:\n"
            code += "  %ret.val = load " + str(t) + "* %ret\n"
            code += "  %elt.ptr = getelementptr " + str(t) + "* %buff, i32 %index\n"
            code += "  %elt = load " + str(t) + "* %elt.ptr\n"
            code += "  %res = call " + str(t) + " %f(" + str(t) + " %ret.val, " + str(t) + " %elt)\n"
            code += "  store " + str(t) + " %res, " + str(t) + "* %ret\n"
            code += "  br label %loopreduce_close\n\n"

            code += "loopreduce_close:\n"
            code += "  %index.next = add i32 %index, 1\n"
            code += "  store i32 %index.next, i32* %i\n"
            code += "  br label %loopreduce_head\n\n"

            code += "loopreduce_exit:\n"
            code += "  %ret.value = load " + str(t) + "* %ret\n"
            code += "  ret " + str(t) + " %ret.value\n"
            code += "}\n\n"
        return code




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
    if t.isArray():
        print (8 if platform.architecture()[0] == "64bit" else 4)
        return 4 + (8 if platform.architecture()[0] == "64bit" else 4) # int + ptr(62/64)
    if t.isArray() or t.isFunction():
        return (8 if platform.architecture() == "64bit" else 4) # ptr(32/64)
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
