# -*- coding: utf-8 -*-

# Compiler written with PLY for a C map/reduce language
# by Florian LE VERN and Sylvain CASSIAU
# at ENSEIRB-Matmeca, Bordeaux, FRANCE
# november 2015

# This script reads a "C M/R" source file and outputs the corresponding llvm
# internal representation which can be compiled by 'llc' to produce a .s file
# and then by 'gcc' to get a binary.



# check python version
import sys
if sys.version_info[0] >= 3:
    raw_input = input
# change directory for generated files
import os
os.chdir("build")



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


# build the lexer
import ply.lex as lex
lex.lex()




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
        self.prev = None
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




# now, we can use this awsome context class
currentContext = Context()
def enterNewContext():
    '''Sets current context as a new context with the previous surrounding context as parent.
    e.g. when entering a { ... } block'''
    nc = Context(currentContext)
    currentContext = nc

def closeCurrentContext():
    '''Set current context back to its parent'''
    if currentContext.isGlobal():
        # is there a best way to raise an error ?
        print "ERROR : trying to close global context"
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


def p_program_2(p):
    '''program : external_declaration'''
    p[0] = {"code" : p[1]["code"] + "\n"}


def p_external_declaration_1(p):
    '''external_declaration : function_definition'''
    p[0] = {"code" : p[1]["code"]}


def p_external_declaration_2(p):
    '''external_declaration : declaration'''
    p[0] = {"code" : ""} #TODO it
    pass

def p_function_definition(p):
    '''function_definition : type_name declarator compound_statement'''
    if currentContext.exists(p[2]["name"]):
        sys.stderr.write("*WARNING* You are redefining "+p[2]["name"]+"\n")
    if not p[2]["type"] is None: # function
        currentContext.setType(p[2]["name"], p[1]["code"]+"("+p[2]["type"]+")")
    else:
        sys.stderr.write("This i not a function declarator\n");
        currentContext.setType(p[2]["name"], p[1]["code"])
    p[0] = {"code" : "define " + p[1]["code"] + " @" + p[2]["code"] + " " + p[3]["code"]}
    pass

def p_type_name_1(p):
    '''type_name : VOID'''
    p[0] = {"type" : "void",
            "code" : "void"}
    pass

def p_type_name_2(p):
    '''type_name : CHAR'''
    p[0] = {"type" : "i8",
            "code" : "i8"}
    pass

def p_type_name_3(p):
    '''type_name : INT'''
    p[0] = {"type" : "i32",
            "code" : "i32"}
    pass

def p_type_name_4(p):
    '''type_name : FLOAT'''
    p[0] = {"type" : "float",
            "code" : "float"}
    pass

def p_type_name_5(p):
    '''type_name : type_name LBRACKET RBRACKET'''
    p[0] = {"code" : ".", # TODO array type
            "type" : p[1]["type"] + "[]"}
    pass

def p_type_name_6(p):
    '''type_name : type_name LBRACKET ICONST RBRACKET'''
    p[0] = {"code" : ".", # TODO array type
            "type" : p[1]["type"] + "[]"} #TODO: store size ?
    pass

def p_declarator_1(p):
    '''declarator : ID'''
    p[0] = {"name" : p[1],
            "type" : None,
            "code" : p[1]}
    pass

## Les déclarators suivants ne sont pas conformes à notre spécification
#def p_declarator_2(p):
#    '''declarator : LPAREN declarator RPAREN'''
#    p[0] = {"name" : p[2]["name"],
#            "type" : p[2]["type"],
#            "code" : p[2]["code"]}
#    pass
#
#def p_declarator_3(p):
#    '''declarator : declarator LBRACKET ICONST RBRACKET'''
#    p[0] = {"name" : p[1]["name"],
#            "type" : p[1]["type"],
#            "code" : p[1]["code"]}
#    pass
#
#def p_declarator_4(p):
#    '''declarator : declarator LBRACKET RBRACKET'''
#    p[0] = {"name" : p[1]["name"], "code" : p[1]["code"]}
#    pass

def p_declarator_5(p):
    '''declarator : declarator LPAREN parameter_list RPAREN'''
    p[0] = {"name" : p[1]["name"],
            "type" : p[3]["type"],
            "code" : p[1]["code"] + "(" + p[3]["code"] +")"}
    pass

def p_declarator_6(p):
    '''declarator : declarator LPAREN RPAREN'''
    p[0] = {"name" : p[1]["name"],
            "type" : "",
            "code" : p[1]["code"] + "()"}
    pass

def p_compound_statement_1(p):
    '''compound_statement : LBRACE RBRACE'''
    p[0] = {"code" : "{}"}
    pass

def p_compound_statement_2(p):
    '''compound_statement : LBRACE statement_list RBRACE'''
    p[0] = {"code" : "{\n...\n}"}
    pass

def p_compound_statement_3(p):
    '''compound_statement : LBRACE declaration_list statement_list RBRACE'''
    p[0] = {"code" : "{\n...\n}"}
    pass

def p_declaration_1(p):
    '''declaration : type_name declarator_list SEMI'''
    p[0] = {"code" : ""}
    pass

def p_declaration_2(p):
    '''declaration : EXTERN type_name declarator_list SEMI'''
    p[0] = {"code" : "declare @..."}
    pass

def p_parameter_list_1(p):
    '''parameter_list : parameter_declaration'''
    p[0] = {"type" : p[1]["type"],
            "code" : p[1]["code"]}
    pass

def p_parameter_list_2(p):
    '''parameter_list : parameter_list COMMA parameter_declaration'''
    p[0] = {"type" : p[1]["type"] + "," + p[3]["type"],
            "code" : p[1]["code"] + ", " + p[3]["code"]}
    pass

def p_parameter_declaration(p):
    '''parameter_declaration : type_name declarator'''
    p[0] = {"type" : p[1]["type"],
            "code" : p[1]["code"] + " %" + p[2]["name"]}
    pass

# ---------------- trié jusque là

def p_primary_expression_id(p):
    '''primary_expression : ID'''
    pass

def p_primary_expression_iconst(p):
    '''primary_expression : ICONST'''
    pass

def p_primary_expression_fconst(p):
    '''primary_expression : FCONST'''
    pass

def p_primary_expression_paren_expr(p):
    '''primary_expression : LPAREN expression RPAREN'''
    pass

def p_primary_expression_map(p):
    '''primary_expression : MAP LPAREN postfix_expression COMMA postfix_expression RPAREN'''
    pass

def p_primary_expression_reduce(p):
    '''primary_expression : REDUCE LPAREN postfix_expression COMMA postfix_expression RPAREN'''
    pass

def p_primary_expression_id_paren(p):
    '''primary_expression : ID LPAREN RPAREN'''
    pass

def p_primary_expression_id_paren_args(p):
    '''primary_expression : ID LPAREN argument_expression_list RPAREN'''
    pass

def p_primary_expression_id_plusplus(p):
    '''primary_expression : ID PLUSPLUS'''
    pass

def p_primary_expression_id_minusminus(p):
    '''primary_expression : ID MINUSMINUS'''
    pass

def p_postfix_expression(p):
    '''postfix_expression : primary_expression
                          | postfix_expression LBRACKET expression RBRACKET'''
    pass

def p_argument_expression_list(p):
    '''argument_expression_list : expression
                                | argument_expression_list COMMA expression'''
    pass

def p_unary_expression(p):
    '''unary_expression : postfix_expression
                        | PLUSPLUS unary_expression
                        | MINUSMINUS unary_expression
                        | unary_operator unary_expression'''
    pass

def p_unary_operator(p):
    '''unary_operator : MINUS'''
    pass

def p_multiplicative_expression(p):
    '''multiplicative_expression : unary_expression
                                  | multiplicative_expression TIMES unary_expression
                                  | multiplicative_expression DIVIDE unary_expression
                                  | multiplicative_expression MOD unary_expression'''
    pass

def p_additive_expression(p):
    '''additive_expression : multiplicative_expression
                           | additive_expression PLUS multiplicative_expression
                           | additive_expression MINUS multiplicative_expression'''
    pass

def p_comparison_expression(p):
    '''comparison_expression : additive_expression
                             | additive_expression LT additive_expression
                             | additive_expression GT additive_expression
                             | additive_expression LE additive_expression
                             | additive_expression GE additive_expression
                             | additive_expression EQ additive_expression
                             | additive_expression NE additive_expression'''
    pass

def p_expression(p):
    '''expression : unary_expression assignment_operator comparison_expression
                  | comparison_expression'''
    pass

def p_assignment_operator(p):
    '''assignment_operator : EQUALS
                           | TIMESEQUAL
                           | DIVEQUAL
                           | MODEQUAL
                           | PLUSEQUAL
                           | MINUSEQUAL'''
    pass

def p_declarator_list(p):
    '''declarator_list : declarator
                       | declarator_list COMMA declarator'''
    pass


def p_statement(p):
    '''statement : compound_statement
                 | expression_statement
                 | selection_statement
                 | iteration_statement
                 | jump_statement'''
    pass

def p_declaration_list(p):
    '''declaration_list : declaration
                        | declaration_list declaration'''
    pass

def p_statement_list(p):
    '''statement_list : statement
                      | statement_list statement'''
    pass

def p_expression_statement(p):
    '''expression_statement : SEMI
                            | expression SEMI'''
    pass

def p_selection_statement(p):
    '''selection_statement : IF LPAREN expression RPAREN statement
                           | IF LPAREN expression RPAREN statement ELSE statement
                           | FOR LPAREN expression_statement expression_statement expression RPAREN statement'''
    pass

def p_iteration_statement(p):
    '''iteration_statement : WHILE LPAREN expression RPAREN statement
                           | DO statement WHILE LPAREN expression RPAREN SEMI'''
    pass

def p_jump_statement(p):
    '''jump_statement : RETURN SEMI
                      | RETURN expression SEMI'''
    pass

def p_error(p):
    if p:
        print("Syntax error at line " + str(p.lineno) + " : '" + p.value + "'")
    else:
        print("Syntax error at EOF")




# build parser
import ply.yacc as yacc
yacc.yacc()



############################   MAIN LOOP   ############################

if __name__ == "__main__":
    import sys
    prog = file("../" + sys.argv[1]).read()
    result = yacc.parse(prog)
    checkGenericErrors(result)
    print result["code"]
