# -*- coding: utf-8 -*-

# Compiler written with PLY for a C map/reduce language
# by Florian LE VERN and Sylvain CASSIAU
# at ENSEIRB-Matmeca, Bordeaux, FRANCE
# november 2015

# This script reads a "C M/R" source file and outputs the corresponding llvm
# internal representation which can be compiled by 'llc' to produce a .s file
# and then by 'gcc' to get a binary.



## check python version
#import sys
#if sys.version_info[0] < 3:
#    sys.stderr.write("*** Please, use at least python 3 ***\n")
#    #exit()
#
## change directory for generated files
#import os
##os.chdir("build")



##############################   LEXER   ##############################


# Reserved words
reserved = (
    'VOID', 'CHAR', 'INT', 'FLOAT',
    'EXTERN',
    'MAP', 'REDUCE',
    'IF', 'ELSE',
    'FOR', 'WHILE', 'DO',
    #'BREAK', 'CONTINUE',
    'RETURN',
    #'SWITCH', 'CASE', 'DEFAULT',
    )

tokens = reserved + (
    # Literals (identifier, integer constant, float constant, string constant, char const)
    'ID', 'ICONST', 'FCONST', # 'SCONST', 'CCONST',

    # Operators (+,-,*,/,%,|,&,~,^,<<,>>, ||, &&, !, <, <=, >, >=, ==, !=)
    'PLUS', 'MINUS', 'TIMES', 'DIVIDE', 'MOD',
    #'OR', 'AND', 'NOT', 'XOR', 'LSHIFT', 'RSHIFT',
    'LOR', 'LAND', 'LNOT',
    'LT', 'LE', 'GT', 'GE', 'EQ', 'NE',

    # Assignment (=, *=, /=, %=, +=, -=, <<=, >>=, &=, ^=, |=)
    'EQUALS', 'TIMESEQUAL', 'DIVEQUAL', 'MODEQUAL', 'PLUSEQUAL', 'MINUSEQUAL',
    #'LSHIFTEQUAL','RSHIFTEQUAL', 'ANDEQUAL', 'XOREQUAL', 'OREQUAL',

    # Increment/decrement (++,--)
    'PLUSPLUS', 'MINUSMINUS',

    # Delimeters ( ) [ ] { } , . ; :
    'LPAREN', 'RPAREN',
    'LBRACKET', 'RBRACKET',
    'LBRACE', 'RBRACE',
    'COMMA', 'SEMI',
    )

# Completely ignored characters
t_ignore           = ' \t\v\f' #\x0c

# Newlines
def t_NEWLINE(t):
    r'\n+'
    t.lexer.lineno += t.value.count("\n")

# Operators
t_PLUS             = r'\+'
t_MINUS            = r'-'
t_TIMES            = r'\*'
t_DIVIDE           = r'/'
t_MOD              = r'%'
#t_OR               = r'\|'
#t_AND              = r'&'
#t_NOT              = r'~'
#t_XOR              = r'\^'
#t_LSHIFT           = r'<<'
#t_RSHIFT           = r'>>'
t_LOR              = r'\|\|'
t_LAND             = r'&&'
t_LNOT             = r'!'
t_LT               = r'<'
t_GT               = r'>'
t_LE               = r'<='
t_GE               = r'>='
t_EQ               = r'=='
t_NE               = r'!='

# Assignment operators

t_EQUALS           = r'='
t_TIMESEQUAL       = r'\*='
t_DIVEQUAL         = r'/='
t_MODEQUAL         = r'%='
t_PLUSEQUAL        = r'\+='
t_MINUSEQUAL       = r'-='
#t_LSHIFTEQUAL      = r'<<='
#t_RSHIFTEQUAL      = r'>>='
#t_ANDEQUAL         = r'&='
#t_OREQUAL          = r'\|='
#t_XOREQUAL         = r'\^='

# Increment/decrement
t_PLUSPLUS         = r'\+\+'
t_MINUSMINUS       = r'--'

# Delimeters
t_LPAREN           = r'\('
t_RPAREN           = r'\)'
t_LBRACKET         = r'\['
t_RBRACKET         = r'\]'
t_LBRACE           = r'\{'
t_RBRACE           = r'\}'
t_COMMA            = r','
#t_PERIOD           = r'\.'
t_SEMI             = r';'

# Identifiers and reserved words

reserved_map = { }
for r in reserved:
    reserved_map[r.lower()] = r


def t_ID(t):
    r'[A-Za-z_][\w_]*'
    t.type = reserved_map.get(t.value,"ID")
    return t

# Integer literal
t_ICONST = r'\d+'

# Floating literal
t_FCONST = r'(\d+)(\.\d+)(e(\+|-)?(\d+))? | (\d+)e(\+|-)?(\d+)'

# String literal
#t_SCONST = r'\"([^\\\n]|(\\.))*?\"'

# Character constant 'c'
#t_CCONST = r'\'([^\\\n]|(\\.))*?\''

# Comments
def t_comment(t):
    r'(/\*(.|\n)*?\*/) | (//.*\n)'
    t.lexer.lineno += t.value.count('\n')

def t_error(t):
    print("Illegal character %s" % repr(t.value[0]))
    t.lexer.skip(1)

# Build the lexer
from ply import lex as lex
lex.lex(outputdir="build")




#############################   PARSER   #############################


# ids and their corresponding types
class Context:
    '''A class to describe ids visibility and their corresponding types'''

    # the surrounding context. If it's None, it means that it's the global context
    prev = None
    # the dictionary associating each id to its type
    id_type = {}

    def __init__(self, c = None):
        '''Creates a new context, with c as surrounding context'''
        self.prev = c
        self.id_type = {}

    def getParent(self):
        '''returns the surrounding context'''
        return self.prev

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


# now, we can use this awsome context class
currentContext = Context()
def enterNewContext():
    '''Sets current context as a new context with the previous surrounding context as parent.
    e.g. when entering a { ... } block'''
    global currentContext
    nc = Context(currentContext)
    currentContext = nc

def closeCurrentContext():
    '''Set current context back to its parent'''
    global currentContext
    if currentContext.isGlobal():
        # is there a best way to raise an error ?
        sys.stderr.write("*ERROR*: trying to close global context")
    else:
        currentContext = currentContext.getParent()



def checkGenericErrors(result):
    '''Check result to throw errors/warnings at the end of the compilation'''
    # look for main
    if not currentContext.exists("main"):
        sys.stderr.write("*WARNING* this program doesn't have a main() function\n")




# first rule because it's the starting symbol
def p_program_1(p):
    '''program : program external_declaration'''
    p[0] = {"code" : p[1]["code"] + "\n" + p[2]["code"] + "\n"}
    #print currentContext.id_type


def p_program_2(p):
    '''program : external_declaration'''
    p[0] = {"code" : p[1]["code"] + "\n"}


def p_external_declaration_1(p):
    '''external_declaration : function_definition'''
    p[0] = {"code" : p[1]["code"]}


def p_external_declaration_2(p):
    '''external_declaration : declaration_statement'''
    p[0] = {"code" : p[1]["code"]} #TODO it
    pass

def p_function_definition(p):
    '''function_definition : type_name function_declarator arguments_declaration compound_statement'''
    if currentContext.exists(p[2]["name"]):
        sys.stderr.write("*WARNING* (l." + str(p.lineno(2)) + "): You are redefining '"+p[2]["name"]+"'\n")
    elif p[2]["name"] in reserved:
        sys.stderr.write("*ERROR* (l." + str(p.lineno(2)) + "): '" + p[2]["name"] + "' is a reseved keyword\n")
        raise SyntaxError
    closeCurrentContext()
    currentContext.setType(p[2]["name"], ["f", [p[1]["type"]]+p[3]["type"]])
    p[0] = {"code" : "define " + p[1]["code"] + " @" + p[2]["name"] + "(" + p[3]["code"] + ") {\n" + p[4]["code"] + "\n}\n"}
    pass

def p_function_declarator(p):
    '''function_declarator : ID'''
    enterNewContext()
    p[0] = {"name" : p[1]}
    pass

def p_arguments_declaration_1(p):
    '''arguments_declaration : LPAREN parameter_list RPAREN'''
    p[0] = {"type" : p[2]["type"],
            "code" : p[2]["code"]}
    pass

def p_arguments_declaration_2(p):
    '''arguments_declaration : LPAREN RPAREN'''
    p[0] = {"type" : [],
            "code" : ""}
    pass

def p_parameter_list_1(p):
    '''parameter_list : parameter_declaration'''
    p[0] = {"type" : [p[1]["type"]],
            "code" : p[1]["code"]}
    pass

def p_parameter_list_2(p):
    '''parameter_list : parameter_list COMMA parameter_declaration'''
    p[0] = {"type" : p[1]["type"] + p[3]["type"],
            "code" : p[1]["code"] + ", " + p[3]["code"]}
    pass

def p_parameter_declaration(p):
    '''parameter_declaration : type_name ID'''
    if currentContext.exists(p[2]):
        sys.stderr.write("*WARNING* (l." + str(p.lineno(2)) + "): You are redefining '" + p[2] + "'\n")
    currentContext.setType(p[2], p[1]["type"]) #TODO : function type
    p[0] = {"type" : p[1]["type"],
            "code" : p[1]["code"] + " %" + p[2]}
    pass

def p_type_name_1(p):
    '''type_name : VOID'''
    p[0] = {"type" : ["v", "void"],
            "code" : "void"}
    pass

def p_type_name_2(p):
    '''type_name : CHAR'''
    p[0] = {"type" : ["v", "i8"],
            "code" : "i8"}
    pass

def p_type_name_3(p):
    '''type_name : INT'''
    p[0] = {"type" : ["v", "i32"],
            "code" : "i32"}
    pass

def p_type_name_4(p):
    '''type_name : FLOAT'''
    p[0] = {"type" : ["v", "float"],
            "code" : "float"}
    pass

def p_type_name_5(p):
    '''type_name : type_name LBRACKET RBRACKET
                 | type_name LBRACKET ICONST RBRACKET'''
    p[0] = {"type" : ["a", p[1]["type"]],
            "code" : p[1]["code"] + "[]"}
    pass

def p_type_name_6(p):
    '''type_name : type_name LPAREN TIMES RPAREN LPAREN type_list RPAREN''' # int(*)(int,char)
    p[0] = {"type" : ["f", [p[1]["type"]]+p[6]["type"] ],
            "code" : "function_type1"}
    pass

def p_type_name_7(p):
    '''type_name : type_name LPAREN TIMES RPAREN LPAREN RPAREN''' # int(*)()
    p[0] = {"type" : ["f", [p[1]["type"]] ],
            "code" : "function_type2"}
    pass

def p_type_list_1(p):
    '''type_list : type_name'''
    p[0] = {"type" : [p[1]["type"]],
            "code" : p[1]["code"]}
    pass

def p_type_list_2(p):
    '''type_list : type_list COMMA type_name'''
    p[0] = {"type" : p[1]["type"] + [p[3]["type"]],
            "code" : p[1]["code"] + ", " + p[3]["code"]}
    pass

def p_compound_statement_1(p):
    '''compound_statement : LBRACE RBRACE'''
    p[0] = {"code" : ""}
    pass

def p_compound_statement_2(p):
    '''compound_statement : LBRACE statement_list RBRACE'''
    p[0] = {"code" : p[2]["code"]}
    pass


def p_declaration_1(p):
    '''declaration_statement : type_name declarator_list SEMI'''
    code = ""
    for d in p[2]: # is a declarator
        if currentContext.exists(d["name"]):
            sys.stderr.write("*WARNING* (l"+str(p.lineno(2))+") : You are redefining " + d["name"]);
        if not d["code"] is None:
            code += d["code"]
        reg = "%reg"
        code += reg + " = alloca " + p[1]["code"] + "\n"
        code += "store " + p[1]["code"] + ", " + p[1]["code"] + "* "
        if not d["code"] is None:
            code += d["reg"]
    p[0] = {"code" : code}
    pass

def p_declaration_2(p):
    '''declaration_statement : EXTERN type_name declarator_list SEMI'''
    p[0] = {"code" : "declare @..."}
    pass

def p_declarator_1(p):
    '''declarator : ID'''
    p[0] = {"name" : p[1],
            "reg" : "%reg",
            "code" : None}
    pass

def p_declarator_2(p):
    '''declarator : ID EQUALS primary_expression'''
    p[0] = {"name" : p[1],
            "reg" : p[3]["reg"],
            "code" : p[3]["code"]}
    pass


# ---------------- trié jusque là

def p_primary_expression_id(p):
    '''primary_expression : ID'''
    p[0] = {"type" : ["v", "i32"],
            "code" : "primary_expression_id",
            "reg" : "registre"}
    pass

def p_primary_expression_iconst(p):
    '''primary_expression : ICONST'''
    p[0] = {"type" : ["v", "i32"], "code" : "primary_expression_iconst", "reg" : "registre"}
    pass

def p_primary_expression_fconst(p):
    '''primary_expression : FCONST'''
    p[0] = {"type" : ["v", "float"], "code" : "primary_expression_fconst", "reg" : "registre"}
    pass

def p_primary_expression_paren_expr(p):
    '''primary_expression : LPAREN expression RPAREN'''
    p[0] = {"type" : p[2]["type"], "code" : "primary_expression_paren_expr", "reg" : "registre"}
    pass

def p_primary_expression_map(p):
    '''primary_expression : MAP LPAREN postfix_expression COMMA postfix_expression RPAREN'''
    p[0] = {"type" : ["a", ["v", "i32"]], "code" : "primary_expression_map", "reg" : "registre"}
    pass

def p_primary_expression_reduce(p):
    '''primary_expression : REDUCE LPAREN postfix_expression COMMA postfix_expression RPAREN'''
    p[0] = {"type" : ["v", "i32"], "code" : "primary_expression_reduce", "reg" : "registre"}
    pass

def p_primary_expression_id_paren(p):
    '''primary_expression : ID LPAREN RPAREN'''
    p[0] = {"type" : ["v", "i32"], "code" : "primary_expression_id_paren", "reg" : "registre"}
    pass

def p_primary_expression_id_paren_args(p):
    '''primary_expression : ID LPAREN argument_expression_list RPAREN'''
    p[0] = {"type" : ["v", "i32"], "code" : "primary_expression_id_paren_args", "reg" : "registre"}
    pass

def p_primary_expression_id_plusplus(p):
    '''primary_expression : ID PLUSPLUS'''
    p[0] = {"type" : ["v", "i32"], "code" : "primary_expression_id_plusplus", "reg" : "registre"}
    pass

def p_primary_expression_id_minusminus(p):
    '''primary_expression : ID MINUSMINUS'''
    p[0] = {"type" : ["v", "i32"], "code" : "primary_expression_id_minusminus", "reg" : "registre"}
    pass

def p_postfix_expression_1(p):
    '''postfix_expression : primary_expression'''
    p[0] = {"type" : p[1]["type"],
            "reg" : p[1]["reg"],
            "code" : p[1]["code"]}
    pass

def p_postfix_expression_2(p):
    '''postfix_expression : postfix_expression LBRACKET expression RBRACKET'''
    p[0] = {"type" : ["v", "i32"],
            "reg" : "newreg",
            "code" : "postfix_expression"}
    pass

def p_argument_expression_list(p):
    '''argument_expression_list : expression
                                | argument_expression_list COMMA expression'''
    pass

def p_unary_expression_1(p):
    '''unary_expression : postfix_expression'''
    p[0] = {"code" : p[1]["code"],
            "type" : p[1]["type"],
            "reg" : p[1]["reg"]}
    pass

def p_unary_expression_2(p):
    '''unary_expression : PLUSPLUS unary_expression'''
    if p[2]["type"][1] == "i32":
        op = "add"
    elif p[2]["type"][1] == "float":
        op = "fadd"

    r1 = newReg()
    r2 = newReg()
    p[0] = {"type" : p[2]["type"],
            "reg" : p[2]["reg"],
            "code" :   p[2]["code"] + "\n"
                     + r1 + " = load " + p[2]["type"][1] + ", " + p[2]["type"][1] + "* " + p[2]["reg"] + "\n"
                     + r2 + " = " + op + " " + p[2]["type"][1] + " " + r1 + ", 1 \n"
                     + "store " + p[2]["type"][1] + " " + r + ", " + p[2]["type"][1] + "* " + p[2]["reg"]}
    pass

def p_unary_expression_3(p):
    '''unary_expression : MINUSMINUS unary_expression'''
    if p[2]["type"][1] == "i32":
        op = "sub"
    elif p[2]["type"][1] == "float":
        op = "fsub"

    r1 = newReg()
    r2 = newReg()
    p[0] = {"type" : p[2]["type"],
            "reg" : p[2]["reg"],
            "code" :   p[2]["code"] + "\n"
                     + r1 + " = load " + p[2]["type"][1] + ", " + p[2]["type"][1] + "* " + p[2]["reg"] + "\n"
                     + r2 + " = " + op + " " + p[2]["type"][1] + " " + r1 + ", 1 \n"
                     + "store " + p[2]["type"][1] + " " + r + ", " + p[2]["type"][1] + "* " + p[2]["reg"]}
    pass

def p_unary_expression_4(p):
    '''unary_expression : MINUS unary_expression'''
    if p[2]["type"][1] == "i32":
        op = "mul"
    elif p[2]["type"][1] == "float":
        op = "fmul"

    r1 = newReg()
    r2 = newReg()
    p[0] = {"type" : p[2]["type"],
            "reg" : p[2]["reg"],
            "code" :   p[2]["code"] + "\n"
                     + r1 + " = load " + p[2]["type"][1] + ", " + p[2]["type"][1] + "* " + p[2]["reg"] + "\n"
                     + r2 + " = " + op + " " + p[2]["type"][1] + " " + r1 + ", -1 \n"
                     + "store " + p[2]["type"][1] + " " + r + ", " + p[2]["type"][1] + "* " + p[2]["reg"]}
    pass

def p_unary_expression_5(p):
    '''unary_expression : LNOT unary_expression'''
    r1 = newReg()
    r2 = newReg()
    r3 = newReg()
    p[0] = {"type" : ["v", "i32"],
            "reg" : r2,
            "code" :   p[2]["code"] + "\n"
                     + r1 + " = load " + p[2]["type"][1] + ", " + p[2]["type"][1] + "* " + p[2]["reg"] + "\n"
                     + r2 + " = icmp eq " + p[2]["type"][1] + " " + r1 + ", 0 \n"
                     + r3 + " = zext i1 " + r2 + " to i32"
            }
    pass

def p_multiplicative_expression_1(p):
    '''multiplicative_expression : unary_expression'''
    p[0] = {"reg" : p[1]["reg"],
            "code" : p[1]["code"],
            "type" : p[1]["type"]}
    pass

def p_multiplicative_expression_2(p):
    '''multiplicative_expression : multiplicative_expression TIMES unary_expression'''
    r1 = newReg()
    r2 = newReg()
    r3 = newReg()
    t = getType(p[1]["type"], p[3]["type"], p.lineno(0))
    if t[1] == "i32":
        op = "mul"
    elif t[1] == "float":
        op = "fmul"

    p[0] = {"reg" : r1,
            "code" : p[1]["code"] + "\n" + p[3]["code"] + "\n"
                   + r2 + " = sext " + p[1]["type"][1] + " " + p[1]["reg"] + " to " + t[1] + "\n"
                   + r3 + " = sext " + p[3]["type"][1] + " " + p[3]["reg"] + " to " + t[1] + "\n" + ""
                   + r1 + " = " + op + " " + t[1] + " " + r2 + ", " + r3,
            "type" : t}
    pass

def p_multiplicative_expression_3(p):
    '''multiplicative_expression : multiplicative_expression DIVIDE unary_expression'''
    p[0] = {"reg" : newReg(),
            "code" : "multiplicative_expression",
            "type" : ["v", "i32"]}
    pass

def p_multiplicative_expression_4(p):
    '''multiplicative_expression : multiplicative_expression MOD unary_expression'''
    p[0] = {"reg" : newReg(),
            "code" : "multiplicative_expression",
            "type" : ["v", "i32"]}
    pass

def p_multiplicative_expression_5(p):
    '''multiplicative_expression : multiplicative_expression LAND unary_expression'''
    p[0] = {"reg" : newReg(),
            "code" : "multiplicative_expression",
            "type" : ["v", "i32"]}
    pass

def p_additive_expression_1(p):
    '''additive_expression : multiplicative_expression'''
    p[0] = {"reg" : p[1]["reg"],
            "code" : p[1]["code"],
            "type" : p[1]["type"]}
    pass

def p_additive_expression_2(p):
    '''additive_expression : additive_expression PLUS multiplicative_expression'''
    r1 = newReg()
    r2 = newReg()
    r3 = newReg()
    t = getType(p[1]["type"], p[3]["type"], p.lineno(0))
    if t[1] == "i32":
        op = "add"
    elif t[1] == "float":
        op = "fadd"

    p[0] = {"reg" : r1,
            "code" : p[1]["code"] + "\n" + p[3]["code"] + "\n"
                   + r2 + " = sext " + p[1]["type"][1] + " " + p[1]["reg"] + " to " + t[1] + "\n"
                   + r3 + " = sext " + p[3]["type"][1] + " " + p[3]["reg"] + " to " + t[1] + "\n" + ""
                   + r1 + " = " + op + " " + t[1] + " " + r2 + ", " + r3,
            "type" : t}
    pass

def p_additive_expression_3(p):
    '''additive_expression : additive_expression MINUS multiplicative_expression'''
    r1 = newReg()
    r2 = newReg()
    r3 = newReg()
    t = getType(p[1]["type"], p[3]["type"], p.lineno(0))
    if t[1] == "i32":
        op = "sub"
    elif t[1] == "float":
        op = "fsub"

    p[0] = {"reg" : r1,
            "code" : p[1]["code"] + "\n" + p[3]["code"] + "\n"
                   + r2 + " = sext " + p[1]["type"][1] + " " + p[1]["reg"] + " to " + t[1] + "\n"
                   + r3 + " = sext " + p[3]["type"][1] + " " + p[3]["reg"] + " to " + t[1] + "\n" + ""
                   + r1 + " = " + op + " " + t[1] + " " + r2 + ", " + r3,
            "type" : t}
    pass

def p_additive_expression_4(p):
    '''additive_expression : additive_expression LOR multiplicative_expression'''
    r1 = newReg()
    r2 = newReg()
    r3 = newReg()
    r4 = newReg()
    r5 = newReg()
    t = getType(p[1]["type"], p[3]["type"], p.lineno(0))
    if t[1] == "i32":
        op = "add"
    elif t[1] == "float":
        op = "fadd"

    p[0] = {"reg" : r1,
            "code" : p[1]["code"] + "\n" + p[3]["code"] + "\n"
                   + r2 + " = sext " + p[1]["type"][1] + " " + p[1]["reg"] + " to " + t[1] + "\n"
                   + r3 + " = sext " + p[3]["type"][1] + " " + p[3]["reg"] + " to " + t[1] + "\n" + ""
                   + r1 + " = " + op + " " + t[1] + " " + r2 + ", " + r3 + "\n"
                   + r4 + " = icmp eq " + t + " " + r1 + ", 0 \n"
                   + r5 + " = zext i1 " + r2 + " to i32",
            "type" : ["v", "i32"]}
    pass

def p_comparison_expression_1(p):
    '''comparison_expression : additive_expression'''
    p[0] = {"reg" : p[1]["reg"],
            "code" : p[1]["code"],
            "type" : p[1]["type"]}
    pass

def p_comparison_expression_2(p):
    '''comparison_expression : additive_expression LT additive_expression'''
    r1 = newReg()
    r2 = newReg()
    p[0] = {"reg" : r2,
            "code" : p[1]["code"] + "\n" + p[3]["code"] + "\n"
                     + r1 + " = icmp slt " + p[1]["type"][1] + " " + p[1]["reg"] + ", " + p[3]["reg"] + "\n"
                     + r2 + " = zext i1 " + r1 + " to i32",
            "type" : ["v", "i32"]}
    pass

def p_comparison_expression_3(p):
    '''comparison_expression : additive_expression GT additive_expression'''
    r1 = newReg()
    r2 = newReg()
    p[0] = {"reg" : r2,
            "code" : p[1]["code"] + "\n" + p[3]["code"] + "\n"
                     + r1 + " = icmp sgt " + p[1]["type"][1] + " " + p[1]["reg"] + ", " + p[3]["reg"] + "\n"
                     + r2 + " = zext i1 " + r1 + " to i32",
            "type" : ["v", "i32"]}
    pass

def p_comparison_expression_4(p):
    '''comparison_expression : additive_expression LE additive_expression'''
    r1 = newReg()
    r2 = newReg()
    p[0] = {"reg" : r2,
            "code" : p[1]["code"] + "\n" + p[3]["code"] + "\n"
                     + r1 + " = icmp sle " + p[1]["type"][1] + " " + p[1]["reg"] + ", " + p[3]["reg"] + "\n"
                     + r2 + " = zext i1 " + r1 + " to i32",
            "type" : ["v", "i32"]}
    pass

def p_comparison_expression_5(p):
    '''comparison_expression : additive_expression GE additive_expression'''
    r1 = newReg()
    r2 = newReg()
    p[0] = {"reg" : r2,
            "code" : p[1]["code"] + "\n" + p[3]["code"] + "\n"
                     + r1 + " = icmp sge " + p[1]["type"][1] + " " + p[1]["reg"] + ", " + p[3]["reg"] + "\n"
                     + r2 + " = zext i1 " + r1 + " to i32",
            "type" : ["v", "i32"]}
    pass

def p_comparison_expression_6(p):
    '''comparison_expression : additive_expression EQ additive_expression'''
    r1 = newReg()
    r2 = newReg()
    p[0] = {"reg" : r2,
            "code" : p[1]["code"] + "\n" + p[3]["code"] + "\n"
                     + r1 + " = icmp eq " + p[1]["type"][1] + " " + p[1]["reg"] + ", " + p[3]["reg"] + "\n"
                     + r2 + " = zext i1 " + r1 + " to i32",
            "type" : ["v", "i32"]}
    pass

def p_comparison_expression_7(p):
    '''comparison_expression : additive_expression NE additive_expression'''
    r1 = newReg()
    r2 = newReg()
    p[0] = {"reg" : r2,
            "code" : p[1]["code"] + "\n" + p[3]["code"] + "\n"
                     + r1 + " = icmp ne " + p[1]["type"][1] + " " + p[1]["reg"] + ", " + p[3]["reg"] + "\n"
                     + r2 + " = zext i1 " + r1 + " to i32",
            "type" : ["v", "i32"]}
    pass


# WARNING !!!! :  faire attention aux variables qui sont des pointeurs llvm ou non
# Faire des load à la création de la variable ?
# Faire un store à l'allocation -> nécessité d'un pointeur
# ?? unary_expression = type* ??

def p_expression_1(p):
    '''expression : unary_expression EQUALS comparison_expression'''
    if p[1]["type"] != p[3]["type"]:
        sys.stderr.write("*ERROR* Incompatible types in operation on line " + str(p.lineno(0)) + "\n")
        raise SyntaxError
    p[0] = {"code" : p[1]["code"] + "\n" + p[3]["code"] + "\n"
                   + "store " + p[3]["type"][1] + " " + p[3]["reg"] + ", " + p[1]["type"][1] + "* " + p[1]["reg"] + "\n",
            "reg" : p[1]["reg"],
            "type" : p[1]["type"]}
    pass

def p_expression_2(p):
    '''expression : unary_expression TIMESEQUAL comparison_expression'''
    t = getType(p[1]["type"], p[3]["type"], p.lineno(0))
    if p[1]["type"] != t:
        sys.stderr.write("*ERROR* Incompatible types in operation on line " + str(p.lineno(0)) + "\n")
        raise SyntaxError
    if t[1] == "i32":
        op = "mul"
    elif t[1] == "float":
        op = "fmul"

    r = newReg()
    p[0] = {"code" : p[1]["code"] + "\n" + p[3]["code"] + "\n"
                   + r + " = " + op + " " + p[1]["type"][1] + " " + p[1]["reg"] + ", " + p[3]["reg"] + "\n"
                   + "store " + p[1]["type"][1] + " " + r + ", " + p[1]["type"][1] + "* " + p[1]["reg"] + "\n",
            "reg" : p[1]["reg"],
            "type" : p[1]["type"]}
    pass

def p_expression_3(p):
    '''expression : unary_expression DIVEQUAL comparison_expression'''
    t = getType(p[1]["type"], p[3]["type"], p.lineno(0))
    if p[1]["type"] != t:
        sys.stderr.write("*ERROR* Incompatible types in operation on line " + str(p.lineno(0)) + "\n")
        raise SyntaxError
    if t[1] == "i32":
        op = "sdiv"
    elif t[1] == "float":
        op = "fdiv"

    r = newReg()
    p[0] = {"code" : p[1]["code"] + "\n" + p[3]["code"] + "\n"
                   + r + " = " + op + " " + p[1]["type"][1] + " " + p[1]["reg"] + ", " + p[3]["reg"] + "\n"
                   + "store " + p[1]["type"][1] + " " + r + ", " + p[1]["type"][1] + "* " + p[1]["reg"] + "\n",
            "reg" : p[1]["reg"],
            "type" : p[1]["type"]}
    pass

def p_expression_4(p):
    '''expression : unary_expression MODEQUAL comparison_expression'''
    p[0] = {"code" : "expression",
            "reg" : "newreg",
            "type" : ["v", "type"]} # TODO
    pass

def p_expression_5(p):
    '''expression : unary_expression PLUSEQUAL comparison_expression'''
    p[0] = {"code" : "expression",
            "reg" : "newreg",
            "type" : ["v", "type"]} # TODO
    pass

def p_expression_6(p):
    '''expression : unary_expression MINUSEQUAL comparison_expression'''
    p[0] = {"code" : "expression",
            "reg" : "newreg",
            "type" : ["v", "type"]} # TODO
    pass

def p_expression_7(p):
    '''expression : comparison_expression'''
    p[0] = {"code" : p[1]["code"] + "\n",
            "reg" : p[1]["reg"],
            "type" : p[1]["type"]}
    pass

def p_declarator_list_1(p):
    '''declarator_list : declarator'''
    p[0] = [p[1]]
    pass

def p_declarator_list_2(p):
    '''declarator_list : declarator_list COMMA declarator'''
    p[0] = p[1] + [p[2]]
    pass


def p_statement(p):
    '''statement : compound_statement
                 | expression_statement
                 | selection_statement
                 | iteration_statement
                 | jump_statement
                 | declaration_statement'''
    p[0] = {"code" : p[1]["code"]}
    pass

def p_statement_list_1(p):
    '''statement_list : statement'''
    p[0] = {"code" : p[1]["code"]}
    pass

def p_statement_list_2(p):
    '''statement_list : statement_list statement'''
    p[0] = {"code" : p[1]["code"] + p[2]["code"]}
    pass

def p_expression_statement_1(p):
    '''expression_statement : SEMI'''
    p[0] = {"code" : "",
            "type" : ["v", None],
            "reg" : None}
    pass
def p_expression_statement_2(p):
    '''expression_statement : expression SEMI'''
    p[0] = {"code" : p[1]["code"],
            "type" : p[1]["type"],
            "reg" : p[1]["reg"]}
    pass

def p_selection_statement_1(p):
    '''selection_statement : IF LPAREN expression RPAREN statement'''
    p[0] = {"code" : "if statement"}
    pass

def p_selection_statement_2(p):
    '''selection_statement : IF LPAREN expression RPAREN statement ELSE statement'''
    p[0] = {"code" : "if-else statement"}
    pass

def p_selection_statement_3(p):
    '''selection_statement : FOR LPAREN expression_statement expression_statement expression RPAREN statement'''
    loop_init = newLab()
    loop_head = newLab()
    loop_body = newLab()
    loop_close = newLab()
    loop_exit = newLab()
    r = newReg()
    p[0] = {"code" : "br label %" + loop_init + "\n"
                     + "\n" + loop_init + ": \n"
                     + p[3]["code"]
                     + "br label %" + loop_head + "\n"
                     + "\n" + loop_head + ": \n"
                     + p[4]["code"]
                     + r + " = icmp eq " + p[4]["type"][1] + " " + p[4]["reg"] + ", 0 \n"
                     + "br i1 " + r + ", label %" + loop_body + ", label %" + loop_exit + "\n"
                     + "\n" + loop_body + ": \n"
                     + p[7]["code"]
                     + "br label %" + loop_close + "\n"
                     + "\n" + loop_close + ": \n"
                     + p[5]["code"]
                     + "br label %" + loop_head + "\n"
                     + "\n" + loop_exit + " : \n",
            "type" : ["v", None],
            "reg" : None
           }
    pass

def p_iteration_statement_1(p):
    '''iteration_statement : WHILE LPAREN expression RPAREN statement'''
    p[0] = {"code" : "while statement"}
    pass

def p_iteration_statement_2(p):
    '''iteration_statement : DO statement WHILE LPAREN expression RPAREN SEMI'''
    p[0] = {"code" : "do-while statement"}
    pass

def p_jump_statement_1(p):
    '''jump_statement : RETURN SEMI'''
    p[0] = {"type" : ["v", "void"],
            "code" : "ret void"}
    pass

def p_jump_statement_2(p):
    '''jump_statement : RETURN expression SEMI'''
    p[0] = {"type" : p[2]["type"],
            "code" : p[2]["code"] + "ret " + p[2]["type"][1] + " " + p[2]["reg"]} #TODO : check pour les pointeurs de fonction
    pass

def p_error(p):
    if p:
        print("Syntax error at line " + str(p.lineno) + " : '" + p.value + "'")
    else:
        print("Syntax error at EOF")




# build parser
from ply import yacc as yacc
yacc.yacc(outputdir="build")



############################   MAIN LOOP   ############################

if __name__ == "__main__":
    import sys
    f = open(sys.argv[1])
    prog = f.read()
    f.close()
    result = yacc.parse(prog)
    checkGenericErrors(result)
    print("\n        ===== CODE =====\n")
    print(result["code"])
