# -*- coding: utf-8 -*-
#
# See DJ_compil.py for full description


#############################   PARSER   #############################
import sys
from tools import *
from scanner import tokens, reserved
#tokens = scanner.tokens
from ply import yacc as yacc

# var table
cc = Context()


# first rule because it's the starting symbol
def p_program_1(p):
    '''program : program external_declaration'''
    p[0] = {"code" : p[1]["code"] + "\n" + p[2]["code"] + "\n"}
    #print cc.id_type


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
    if cc.exists(p[2]["name"]):
        warning(p.lineno(2), "You are redefining '"+p[2]["name"]+"'")
    elif p[2]["name"] in reserved:
        error(p.lineno(2), "'"+p[2]["name"]+"' is a reseved keyword")
    cc.close()
    cc.setType(p[2]["name"], ["f", [p[1]["type"]]+p[3]["type"]])
    p[0] = {"code" : "define " + p[1]["code"] + " @" + p[2]["name"] + "(" + p[3]["code"] + ") {\n" + p[4]["code"] + "\n}\n"}
    pass

def p_function_declarator(p):
    '''function_declarator : ID'''
    cc.new()
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
    if cc.exists(p[2]):
        warning(p.lineno(2), "You are redefining '" + p[2] + "'")
    cc.setType(p[2], p[1]["type"]) #TODO : function type
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
        if cc.exists(d["name"]):
            warning(p.lineno(2), "You are redefining " + d["name"]);
        reg = newReg()
        code += reg + " = alloca " + p[1]["code"] + "\n"
        cc.setType(d["name"], p[1]["type"])
        cc.setAddr(d["name"], reg)
        if not d["code"] is None:
            code += d["code"]
            code += "store " + p[1]["code"] + " " + d["reg"] + ", " + p[1]["code"] + "* " + reg + "\n"
    p[0] = {"code" : code,
            "type" : p[1]["type"]}
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

# WARNING !! Faire attention dans les opérations aux registres qui contiennent un pointeur ou une valeur

def p_primary_expression_id(p):
    '''primary_expression : ID'''
    if not cc.exists(p[1]):
        print(cc.id_type)
        error(p.lineno(1), "The expression '" + p[1] + "' is not defined")
        #r = newReg()
        #t = ["v", None]
        #code = "primary_expression_id"
    reg = newReg()
    r = "%addr"#cc.getAddr(p[1])
    t = cc.getType(p[1])
    code = ""
    if t[0] == "v":
        code = reg + " = load " + t[1] + ", " + t[1] + "* " + r
    else: # function, array
        pass

    p[0] = {#"name" : p[1],
            "type" : t,
            "code" : code,
            "reg" : reg}
    pass

def p_primary_expression_iconst(p):
    '''primary_expression : ICONST'''
    p[0] = {"type" : ["v", "i32"],
            "code" : "primary_expression_iconst",
            "reg" : None}
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
            "reg" : r3,
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
    t = getType(p[1]["type"], p[3]["type"], p.lineno(0))
    r1 = newReg()
    r2 = newReg()
    r3 = newReg()
    r4 = newReg()
    if t[1] == "i32" or t[1] == "i8":
        op = "mul"
    elif t[1] == "float":
        op = "fmul"

    p[0] = {"reg" : r4,
            "code" : p[1]["code"] + "\n" + p[3]["code"] + "\n"
                   + r1 + " = load " + p[3]["type"][1] + ", " + p[3]["type"][1] + "* " + p[3]["reg"] + "\n"
                   + r2 + " = sext " + p[1]["type"][1] + " " + p[1]["reg"] + " to " + t[1] + "\n"
                   + r3 + " = sext " + p[3]["type"][1] + " " + r1 + " to " + t[1] + "\n"
                   + r4 + " = " + op + " " + t[1] + " " + r2 + ", " + r3,
            "type" : t}
    pass

def p_multiplicative_expression_3(p):
    '''multiplicative_expression : multiplicative_expression DIVIDE unary_expression'''
    t = getType(p[1]["type"], p[3]["type"], p.lineno(0))
    r1 = newReg()
    r2 = newReg()
    r3 = newReg()
    r4 = newReg()
    if t[1] == "i32" or t[1] == "i8":
        op = "sdiv"
    elif t[1] == "float":
        op = "fdiv"

    p[0] = {"reg" : r4,
            "code" : p[1]["code"] + "\n" + p[3]["code"] + "\n"
                   + r1 + " = load " + p[3]["type"][1] + ", " + p[3]["type"][1] + "* " + p[3]["reg"] + "\n"
                   + r2 + " = sext " + p[1]["type"][1] + " " + p[1]["reg"] + " to " + t[1] + "\n"
                   + r3 + " = sext " + p[3]["type"][1] + " " + r1 + " to " + t[1] + "\n"
                   + r4 + " = " + op + " " + t[1] + " " + r2 + ", " + r3,
            "type" : t}
    pass

def p_multiplicative_expression_4(p):
    '''multiplicative_expression : multiplicative_expression MOD unary_expression'''
    t = getType(p[1]["type"], p[3]["type"], p.lineno(0))
    r1 = newReg()
    r2 = newReg()
    r3 = newReg()
    r4 = newReg()
    if t[1] == "i32" or t[1] == "i8":
        op = "srem"
    elif t[1] == "float":
        op = "frem"

    p[0] = {"reg" : r4,
            "code" : p[1]["code"] + "\n" + p[3]["code"] + "\n"
                   + r1 + " = load " + p[3]["type"][1] + ", " + p[3]["type"][1] + "* " + p[3]["reg"] + "\n"
                   + r2 + " = sext " + p[1]["type"][1] + " " + p[1]["reg"] + " to " + t[1] + "\n"
                   + r3 + " = sext " + p[3]["type"][1] + " " + r1 + " to " + t[1] + "\n"
                   + r4 + " = " + op + " " + t[1] + " " + r2 + ", " + r3,
            "type" : t}
    pass

def p_multiplicative_expression_5(p):
    '''multiplicative_expression : multiplicative_expression LAND unary_expression'''
    t = getType(p[1]["type"], p[3]["type"], p.lineno(0))
    r1 = newReg()
    r2 = newReg()
    r3 = newReg()
    r4 = newReg()
    r5 = newReg()
    r6 = newReg()
    if t[1] == "i32" or t[1] == "i8":
        op = "mul"
    elif t[1] == "float":
        op = "fmul"

    p[0] = {"reg" : r6,
            "code" : p[1]["code"] + "\n" + p[3]["code"] + "\n"
                   + r1 + " = load " + p[3]["type"][1] + ", " + p[3]["type"][1] + "* " + p[3]["reg"] + "\n"
                   + r2 + " = sext " + p[1]["type"][1] + " " + p[1]["reg"] + " to " + t[1] + "\n"
                   + r3 + " = sext " + p[3]["type"][1] + " " + r1 + " to " + t[1] + "\n"
                   + r4 + " = " + op + " " + t[1] + " " + r2 + ", " + r3 + "\n"
                   + r5 + " = icmp eq " + t[1] + " " + r4 + ", 0 \n"
                   + r6 + " = zext i1 " + r5 + " to i32",
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
    t = getType(p[1]["type"], p[3]["type"], p.lineno(0))
    r1 = newReg()
    r2 = newReg()
    r3 = newReg()
    if t[1] == "i32" or t[1] == "i8":
        op = "add"
    elif t[1] == "float":
        op = "fadd"

    p[0] = {"reg" : r1,
            "code" : p[1]["code"] + "\n" + p[3]["code"] + "\n"
                   + r2 + " = sext " + p[1]["type"][1] + " " + p[1]["reg"] + " to " + t[1] + "\n"
                   + r3 + " = sext " + p[3]["type"][1] + " " + p[3]["reg"] + " to " + t[1] + "\n"
                   + r1 + " = " + op + " " + t[1] + " " + r2 + ", " + r3,
            "type" : t}
    pass

def p_additive_expression_3(p):
    '''additive_expression : additive_expression MINUS multiplicative_expression'''
    t = getType(p[1]["type"], p[3]["type"], p.lineno(0))
    r1 = newReg()
    r2 = newReg()
    r3 = newReg()
    if t[1] == "i32" or t[1] == "i8":
        op = "sub"
    elif t[1] == "float":
        op = "fsub"

    p[0] = {"reg" : r1,
            "code" : p[1]["code"] + "\n" + p[3]["code"] + "\n"
                   + r2 + " = sext " + p[1]["type"][1] + " " + p[1]["reg"] + " to " + t[1] + "\n"
                   + r3 + " = sext " + p[3]["type"][1] + " " + p[3]["reg"] + " to " + t[1] + "\n"
                   + r1 + " = " + op + " " + t[1] + " " + r2 + ", " + r3,
            "type" : t}
    pass

def p_additive_expression_4(p):
    '''additive_expression : additive_expression LOR multiplicative_expression'''
    t = getType(p[1]["type"], p[3]["type"], p.lineno(0))
    r1 = newReg()
    r2 = newReg()
    r3 = newReg()
    r4 = newReg()
    r5 = newReg()
    if t[1] == "i32" or t[1] == "i8":
        op = "add"
    elif t[1] == "float":
        op = "fadd"

    p[0] = {"reg" : r1,
            "code" : p[1]["code"] + "\n" + p[3]["code"] + "\n"
                   + r2 + " = sext " + p[1]["type"][1] + " " + p[1]["reg"] + " to " + t[1] + "\n"
                   + r3 + " = sext " + p[3]["type"][1] + " " + p[3]["reg"] + " to " + t[1] + "\n"
                   + r1 + " = " + op + " " + t[1] + " " + r2 + ", " + r3 + "\n"
                   + r4 + " = icmp eq " + t[1] + " " + r1 + ", 0 \n"
                   + r5 + " = zext i1 " + r4 + " to i32",
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
    t = getType(p[1]["type"], p[3]["type"], p.lineno(0))
    r1 = newReg()
    r2 = newReg()
    r3 = newReg()
    r4 = newReg()
    p[0] = {"reg" : r3,
            "code" : p[1]["code"] + "\n" + p[3]["code"] + "\n"
                     + r1 + " = sext " + p[1]["type"][1] + " " + p[1]["reg"] + " to " + t[1] + "\n"
                     + r2 + " = sext " + p[3]["type"][1] + " " + p[3]["reg"] + " to " + t[1] + "\n"
                     + r3 + " = icmp slt " + t[1] + " " + r1 + ", " + r2 + "\n"
                     + r4 + " = zext i1 " + r3 + " to i32",
            "type" : ["v", "i32"]}
    pass

def p_comparison_expression_3(p):
    '''comparison_expression : additive_expression GT additive_expression'''
    t = getType(p[1]["type"], p[3]["type"], p.lineno(0))
    r1 = newReg()
    r2 = newReg()
    r3 = newReg()
    r4 = newReg()
    p[0] = {"reg" : r3,
            "code" : p[1]["code"] + "\n" + p[3]["code"] + "\n"
                     + r1 + " = sext " + p[1]["type"][1] + " " + p[1]["reg"] + " to " + t[1] + "\n"
                     + r2 + " = sext " + p[3]["type"][1] + " " + p[3]["reg"] + " to " + t[1] + "\n"
                     + r3 + " = icmp sgt " + t[1] + " " + r1 + ", " + r2 + "\n"
                     + r4 + " = zext i1 " + r3 + " to i32",
            "type" : ["v", "i32"]}
    pass

def p_comparison_expression_4(p):
    '''comparison_expression : additive_expression LE additive_expression'''
    t = getType(p[1]["type"], p[3]["type"], p.lineno(0))
    r1 = newReg()
    r2 = newReg()
    r3 = newReg()
    r4 = newReg()
    p[0] = {"reg" : r3,
            "code" : p[1]["code"] + "\n" + p[3]["code"] + "\n"
                     + r1 + " = sext " + p[1]["type"][1] + " " + p[1]["reg"] + " to " + t[1] + "\n"
                     + r2 + " = sext " + p[3]["type"][1] + " " + p[3]["reg"] + " to " + t[1] + "\n"
                     + r3 + " = icmp sle " + t[1] + " " + r1 + ", " + r2 + "\n"
                     + r4 + " = zext i1 " + r3 + " to i32",
            "type" : ["v", "i32"]}
    pass

def p_comparison_expression_5(p):
    '''comparison_expression : additive_expression GE additive_expression'''
    t = getType(p[1]["type"], p[3]["type"], p.lineno(0))
    r1 = newReg()
    r2 = newReg()
    r3 = newReg()
    r4 = newReg()
    p[0] = {"reg" : r3,
            "code" : p[1]["code"] + "\n" + p[3]["code"] + "\n"
                     + r1 + " = sext " + p[1]["type"][1] + " " + p[1]["reg"] + " to " + t[1] + "\n"
                     + r2 + " = sext " + p[3]["type"][1] + " " + p[3]["reg"] + " to " + t[1] + "\n"
                     + r3 + " = icmp sge " + t[1] + " " + r1 + ", " + r2 + "\n"
                     + r4 + " = zext i1 " + r3 + " to i32",
            "type" : ["v", "i32"]}
    pass

def p_comparison_expression_6(p):
    '''comparison_expression : additive_expression EQ additive_expression'''
    t = getType(p[1]["type"], p[3]["type"], p.lineno(0))
    r1 = newReg()
    r2 = newReg()
    r3 = newReg()
    r4 = newReg()
    p[0] = {"reg" : r3,
            "code" : p[1]["code"] + "\n" + p[3]["code"] + "\n"
                     + r1 + " = sext " + p[1]["type"][1] + " " + p[1]["reg"] + " to " + t[1] + "\n"
                     + r2 + " = sext " + p[3]["type"][1] + " " + p[3]["reg"] + " to " + t[1] + "\n"
                     + r3 + " = icmp eq " + t[1] + " " + r1 + ", " + r2 + "\n"
                     + r4 + " = zext i1 " + r3 + " to i32",
            "type" : ["v", "i32"]}
    pass

def p_comparison_expression_7(p):
    '''comparison_expression : additive_expression NE additive_expression'''
    t = getType(p[1]["type"], p[3]["type"], p.lineno(0))
    r1 = newReg()
    r2 = newReg()
    r3 = newReg()
    r4 = newReg()
    p[0] = {"reg" : r3,
            "code" : p[1]["code"] + "\n" + p[3]["code"] + "\n"
                     + r1 + " = sext " + p[1]["type"][1] + " " + p[1]["reg"] + " to " + t[1] + "\n"
                     + r2 + " = sext " + p[3]["type"][1] + " " + p[3]["reg"] + " to " + t[1] + "\n"
                     + r3 + " = icmp ne " + t[1] + " " + r1 + ", " + r2 + "\n"
                     + r4 + " = zext i1 " + r3 + " to i32",
            "type" : ["v", "i32"]}
    pass

def p_expression_1(p):
    '''expression : unary_expression EQUALS comparison_expression'''
    if p[1]["type"] != p[3]["type"]:
        error(p.lineno(0), "Incompatible types in operation")
    p[0] = {"code" : p[1]["code"] + "\n" + p[3]["code"] + "\n"
                   + "store " + p[3]["type"][1] + " " + p[3]["reg"] + ", " + p[1]["type"][1] + "* " + p[1]["reg"] + "\n",
            "reg" : p[1]["reg"],
            "type" : p[1]["type"]}
    pass

def p_expression_2(p):
    '''expression : unary_expression TIMESEQUAL comparison_expression'''
    t = getType(p[1]["type"], p[3]["type"], p.lineno(0))
    if p[1]["type"] != t:
        error(p.lineno(0), "Incompatible types in operation")
        raise SyntaxError
    if t[1] == "i32" or t[1] == "i8":
        op = "mul"
    elif t[1] == "float":
        op = "fmul"

    r1 = newReg()
    r2 = newReg()
    p[0] = {"code" : p[1]["code"] + "\n" + p[3]["code"] + "\n"
                   + r1 + " = load " + p[1]["type"][1] + ", " + p[1]["type"][1] + "* " + p[1]["reg"] + "\n"
                   + r2 + " = " + op + " " + p[1]["type"][1] + " " + r1 + ", " + p[3]["reg"] + "\n"
                   + "store " + p[1]["type"][1] + " " + r + ", " + p[1]["type"][1] + "* " + p[1]["reg"] + "\n",
            "reg" : p[1]["reg"],
            "type" : p[1]["type"]}
    pass

def p_expression_3(p):
    '''expression : unary_expression DIVEQUAL comparison_expression'''
    t = getType(p[1]["type"], p[3]["type"], p.lineno(0))
    if p[1]["type"] != t:
        error(p.lineno(0), "Incompatible types in operation")
    if t[1] == "i32" or t[1] == "i8":
        op = "sdiv"
    elif t[1] == "float":
        op = "fdiv"

    r1 = newReg()
    r2 = newReg()
    p[0] = {"code" : p[1]["code"] + "\n" + p[3]["code"] + "\n"
                   + r1 + " = load " + p[1]["type"][1] + ", " + p[1]["type"][1] + "* " + p[1]["reg"] + "\n"
                   + r2 + " = " + op + " " + p[1]["type"][1] + " " + r1 + ", " + p[3]["reg"] + "\n"
                   + "store " + p[1]["type"][1] + " " + r + ", " + p[1]["type"][1] + "* " + p[1]["reg"] + "\n",
            "reg" : p[1]["reg"],
            "type" : p[1]["type"]}
    pass

def p_expression_4(p):
    '''expression : unary_expression MODEQUAL comparison_expression'''
    t = getType(p[1]["type"], p[3]["type"], p.lineno(0))
    if p[1]["type"] != t:
        error(p.lineno(0), "Incompatible types in operation")
    if t[1] == "i32" or t[1] == "i8":
        op = "srem"
    elif t[1] == "float":
        op = "frem"

    r1 = newReg()
    r2 = newReg()
    p[0] = {"code" : p[1]["code"] + "\n" + p[3]["code"] + "\n"
                   + r1 + " = load " + p[1]["type"][1] + ", " + p[1]["type"][1] + "* " + p[1]["reg"] + "\n"
                   + r2 + " = " + op + " " + p[1]["type"][1] + " " + r1 + ", " + p[3]["reg"] + "\n"
                   + "store " + p[1]["type"][1] + " " + r + ", " + p[1]["type"][1] + "* " + p[1]["reg"] + "\n",
            "reg" : p[1]["reg"],
            "type" : p[1]["type"]}
    pass

def p_expression_5(p):
    '''expression : unary_expression PLUSEQUAL comparison_expression'''
    t = getType(p[1]["type"], p[3]["type"], p.lineno(0))
    if p[1]["type"] != t:
        error(p.lineno(0), "Incompatible types in operation")
    if t[1] == "i32" or t[1] == "i8":
        op = "add"
    elif t[1] == "float":
        op = "fadd"

    r1 = newReg()
    r2 = newReg()
    p[0] = {"code" : p[1]["code"] + "\n" + p[3]["code"] + "\n"
                   + r1 + " = load " + p[1]["type"][1] + ", " + p[1]["type"][1] + "* " + p[1]["reg"] + "\n"
                   + r2 + " = " + op + " " + p[1]["type"][1] + " " + r1 + ", " + p[3]["reg"] + "\n"
                   + "store " + p[1]["type"][1] + " " + r + ", " + p[1]["type"][1] + "* " + p[1]["reg"] + "\n",
            "reg" : p[1]["reg"],
            "type" : p[1]["type"]}
    pass

def p_expression_6(p):
    '''expression : unary_expression MINUSEQUAL comparison_expression'''
    t = getType(p[1]["type"], p[3]["type"], p.lineno(0))
    if p[1]["type"] != t:
        error(p.lineno(0), "Incompatible types in operation")
    if t[1] == "i32" or t[1] == "i8":
        op = "sub"
    elif t[1] == "float":
        op = "fsub"

    r1 = newReg()
    r2 = newReg()
    p[0] = {"code" : p[1]["code"] + "\n" + p[3]["code"] + "\n"
                   + r1 + " = load " + p[1]["type"][1] + ", " + p[1]["type"][1] + "* " + p[1]["reg"] + "\n"
                   + r2 + " = " + op + " " + p[1]["type"][1] + " " + r1 + ", " + p[3]["reg"] + "\n"
                   + "store " + p[1]["type"][1] + " " + r + ", " + p[1]["type"][1] + "* " + p[1]["reg"] + "\n",
            "reg" : p[1]["reg"],
            "type" : p[1]["type"]}
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

yacc.yacc(outputdir="build") #debug=0
