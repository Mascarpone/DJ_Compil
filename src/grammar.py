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
    p[0] = {"code" : p[1]["code"]}

def p_external_declaration_3(p):
    '''external_declaration : EXTERN declaration_statement'''
    p[0] = {"code" : "declare " + p[2]["code"]}

def p_external_declaration_4(p):
    '''external_declaration : EXTERN type_name function_declarator arguments_declaration SEMI'''
    # function_declarator open a new context that must be closed
    cc.close()
    cc.setType(p[3]["name"], ["f", [p[2]["type"]]+p[4]["type"]])
    p[0] = {"code" : "declare " + p[2]["code"] + " @" + p[3]["name"] + "(" + p[4]["code"] + ")"}
    pass

def p_function_definition(p):
    '''function_definition : type_name function_declarator arguments_declaration compound_statement'''
    if cc.exists(p[2]["name"]):
        warning(p.lineno(2), "You are redefining '"+p[2]["name"]+"'")
    elif p[2]["name"] in reserved:
        error(p.lineno(2), "'"+p[2]["name"]+"' is a reseved keyword")
    cc.close()
    cc.setType(p[2]["name"], ["f", [p[1]["type"]]+p[3]["type"]])

    code = "define " + p[1]["code"] + " @" + p[2]["name"] + "(" + p[3]["code"] + ") {\n"
    code += p[3]["init"]
    code += p[4]["code"] + "\n}\n"

    p[0] = {"code" : code}
    pass

def p_function_declarator(p):
    '''function_declarator : ID'''
    cc.new()
    p[0] = {"name" : p[1]}
    pass

def p_arguments_declaration_1(p):
    '''arguments_declaration : LPAREN parameter_list RPAREN'''
    init = ""
    for t, n in zip(p[2]["type"], p[2]["name"]):
        cc.setType(n, t)
        cc.setAddr(n, "%" + n[0])
        init += "%" + n + " = alloca " + t[1] + "\n"
        init += "store " + t[1] + " %" + n + "arg, " + t[1] + "* %" + n + "\n"
    p[0] = {"type" : p[2]["type"],
            "code" : p[2]["code"],
            "init" : init}
    pass

def p_arguments_declaration_2(p):
    '''arguments_declaration : LPAREN RPAREN'''
    p[0] = {"type" : [],
            "code" : "",
            "init" : ""}
    pass

def p_parameter_list_1(p):
    '''parameter_list : parameter_declaration'''
    p[0] = {"type" : [p[1]["type"]],
            "code" : p[1]["code"],
            "name" : [p[1]["name"]]}
    pass

def p_parameter_list_2(p):
    '''parameter_list : parameter_list COMMA parameter_declaration'''
    p[0] = {"type" : p[1]["type"] + [p[3]["type"]],
            "code" : p[1]["code"] + ", " + p[3]["code"],
            "name" : p[1]["name"] + [p[3]["name"]]}
    pass

def p_parameter_declaration(p):
    '''parameter_declaration : type_name ID'''
    if cc.exists(p[2]):
        warning(p.lineno(2), "You are redefining '" + p[2] + "'")
    cc.setType(p[2], p[1]["type"])

    p[0] = {"type" : p[1]["type"],
            "code" : p[1]["code"] + " %" + p[2] + "arg",
            "name" : p[2]}
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
        if d["code"] is not None:
            code += d["code"]
            code += "store " + p[1]["code"] + " " + d["reg"] + ", " + p[1]["code"] + "* " + reg + "\n"
    p[0] = {"code" : code,
            "type" : p[1]["type"]}
    pass

def p_declarator_1(p):
    '''declarator : ID'''
    r = "0" #default value ??
    p[0] = {"name" : p[1],
            "reg" : r,
            "code" : ""}
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
    if not cc.exists(p[1]):
        print(cc.id_type)
        error(p.lineno(1), "The expression '" + p[1] + "' is not defined")
    r = cc.getAddr(p[1])
    t = cc.getType(p[1])

    reg = newReg()

    p[0] = {"type" : t,
            "code" : reg + " = load " + t[1] + "* " + r + "\n",
            "reg" : reg,
            "addr" : r}
    pass

def p_primary_expression_iconst(p):
    '''primary_expression : ICONST'''
    p[0] = {"type" : ["v", "i32"], "code" : "", "reg" : p[1]}
    pass

def p_primary_expression_fconst(p):
    '''primary_expression : FCONST'''
    p[0] = {"type" : ["v", "float"], "code" : "", "reg" : float_to_hex(float(p[1]))}
    pass

def p_primary_expression_sconst(p):
    '''primary_expression : SCONST'''
    s = newGBVar()
    l = len(p[1]) - 2
    #setGB(s + " = internal constant [" + str(l) + " x i8] c" + p[1])
    reg = "getelementptr([" + str(l) + " x i8]* " + s + ", i32 0, i32 0)"
    p[0] = {"type" : ["a", ["v", "i8"]], "code" : "", "reg" : reg}
    pass

def p_primary_expression_paren_expr(p):
    '''primary_expression : LPAREN expression RPAREN'''
    p[0] = {"type" : p[2]["type"], "code" : p[2]["code"], "reg" : p[2]["reg"]}
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
    if not cc.exists(p[1]):
        error(p.lineno(1), "The expression '" + p[1] + "' is not defined")
    t = cc.getType(p[1])
    if t[1][0][1] == "void":
        code = "call " + t[1][0][1] + " @" + p[1] + "()" + "\n"
        reg = None
    else:
        r1 = newReg()
        code = r1 + " = call " + t[1][0][1] + " @" + p[1] + "()" + "\n"
        reg = r1
    p[0] = {"type" : t, "code" : code, "reg" : reg}
    pass

def p_primary_expression_id_paren_args(p):
    '''primary_expression : ID LPAREN argument_expression_list RPAREN'''
    if not cc.exists(p[1]):
        error(p.lineno(1), "The expression '" + p[1] + "' is not defined")
    t = cc.getType(p[1])

    code = p[3]["code"]
    if t[1][0][1] == "void":
        code += "call " + t[1][0][1] + " @" + p[1] + "("
        for r, ty in zip(p[3]["reg"], p[3]["type"]):
            if ty[0] == "v":
                code += ty[1] + " " + r
            elif ty[0] == "f": #function
                code += ty[1][0][1] + " " + r
            else: #array
                code += ty[1][1] + "* " + r
        code += ")\n"
        reg = None
    else:
        r1 = newReg()
        code += r1 + " = call " + t[1][0][1] + " @" + p[1] + "("
        args = []
        for r, ty in zip(p[3]["reg"], p[3]["type"]):
            if ty[0] == "v":
                args += [ty[1] + " " + r]
            else: #functions
                args += [ty[1][0][1] + " " + r]
        code += ", ".join(args)
        code += ")\n"
        reg = r1

    p[0] = {"type" : t, "code" : code, "reg" : reg}
    pass

def p_primary_expression_id_plusplus(p):
    '''primary_expression : ID PLUSPLUS'''
    if not cc.exists(p[1]):
        error(p.lineno(1), "The expression '" + p[1] + "' is not defined")
    t = cc.getType(p[1])
    if t[1] == "i32" or t[1] == "i8":
        op = "add"
    elif t[1] == "float":
        op = "fadd"

    r = cc.getAddr(p[1])
    r1 = newReg()
    r2 = newReg()
    p[0] = {"type" : t,
            "reg" : r,
            "code" :   r1 + " = load " + t[1] + "* " + r + "\n"
                     + r2 + " = " + op + " " + t[1] + " " + r1 + ", 1 \n"
                     + "store " + t[1] + " " + r2 + ", " + t[1] + "* " + r + "\n"}
    pass

def p_primary_expression_id_minusminus(p):
    '''primary_expression : ID MINUSMINUS'''
    if not cc.exists(p[1]):
        error(p.lineno(1), "The expression '" + p[1] + "' is not defined")
    t = cc.getType(p[1])
    if t[1] == "i32" or t[1] == "i8":
        op = "sub"
    elif t[1] == "float":
        op = "fsub"

    r = cc.getAddr(p[1])
    r1 = newReg()
    r2 = newReg()
    p[0] = {"type" : t,
            "reg" : r,
            "code" :   r1 + " = load " + t[1] + "* " + r + "\n"
                     + r2 + " = " + op + " " + t[1] + " " + r1 + ", 1 \n"
                     + "store " + t[1] + " " + r2 + ", " + t[1] + "* " + r}
    pass

def p_postfix_expression_1(p):
    '''postfix_expression : primary_expression'''
    p[0] = {"type" : p[1]["type"],
            "reg" : p[1]["reg"],
            "code" : p[1]["code"],
            "addr" : p[1]["addr"] if "addr" in p[1] else None}
    pass

def p_postfix_expression_2(p):
    '''postfix_expression : postfix_expression LBRACKET expression RBRACKET'''
    p[0] = {"type" : ["v", "i32"],
            "reg" : "newreg",
            "code" : "postfix_expression:table"}
    pass

def p_argument_expression_list_1(p):
    '''argument_expression_list : expression'''
    p[0] = {"code" : p[1]["code"], "type" : [p[1]["type"]], "reg" : [p[1]["reg"]]}
    pass

def p_argument_expression_list_2(p):
    '''argument_expression_list : argument_expression_list COMMA expression'''
    p[0] = {"code" : p[1]["code"] + p[3]["code"], "type" : p[1]["type"] + [p[3]["type"]], "reg" : p[1]["reg"] + [p[3]["reg"]]}
    pass

def p_unary_expression_1(p):
    '''unary_expression : postfix_expression'''
    p[0] = {"code" : p[1]["code"], "type" : p[1]["type"], "reg" : p[1]["reg"], "addr" : p[1]["addr"]}
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
            "code" :   p[2]["code"]
                     + r1 + " = load " + p[2]["type"][1] + "* " + p[2]["reg"] + "\n"
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
            "code" :   p[2]["code"]
                     + r1 + " = load " + p[2]["type"][1] + "* " + p[2]["reg"] + "\n"
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
            "code" :   p[2]["code"]
                     + r1 + " = load " + p[2]["type"][1] + "* " + p[2]["reg"] + "\n"
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
            "code" :   p[2]["code"]
                     + r1 + " = load " + p[2]["type"][1] + "* " + p[2]["reg"] + "\n"
                     + r2 + " = icmp eq " + p[2]["type"][1] + " " + r1 + ", 0 \n"
                     + r3 + " = zext i1 " + r2 + " to i32\n"
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
    if t[1] == "i32" or t[1] == "i8":
        op = "mul"
    elif t[1] == "float":
        op = "fmul"
    code = p[1]["code"] + p[3]["code"]
    r1 = p[1]["reg"]
    r2 = p[3]["reg"]

    if p[1]["type"] != t:
        r1 = newReg()
        code += r1 + " = sext " + p[1]["type"][1] + " " + p[1]["reg"] + " to " + t[1] + "\n"
    if p[3]["type"] != t:
        r2 = newReg()
        code += r2 + " = sext " + p[3]["type"][1] + " " + p[3]["reg"] + " to " + t[1] + "\n"

    r3 = newReg()

    p[0] = {"reg" : r3,
            "code" : code + r3 + " = " + op + " " + t[1] + " " + r1 + ", " + r2 + "\n",
            "type" : t}
    pass

def p_multiplicative_expression_3(p):
    '''multiplicative_expression : multiplicative_expression DIVIDE unary_expression'''
    t = getType(p[1]["type"], p[3]["type"], p.lineno(0))
    if t[1] == "i32" or t[1] == "i8":
        op = "sdiv"
    elif t[1] == "float":
        op = "fdiv"

    code = p[1]["code"] + p[3]["code"]
    r1 = p[1]["reg"]
    r2 = p[3]["reg"]

    if p[1]["type"] != t:
        r1 = newReg()
        code += r1 + " = sext " + p[1]["type"][1] + " " + p[1]["reg"] + " to " + t[1] + "\n"
    if p[3]["type"] != t:
        r2 = newReg()
        code += r2 + " = sext " + p[3]["type"][1] + " " + p[3]["reg"] + " to " + t[1] + "\n"

    r3 = newReg()

    p[0] = {"reg" : r3,
            "code" : code + r3 + " = " + op + " " + t[1] + " " + r1 + ", " + r2 + "\n",
            "type" : t}
    pass

def p_multiplicative_expression_4(p):
    '''multiplicative_expression : multiplicative_expression MOD unary_expression'''
    t = getType(p[1]["type"], p[3]["type"], p.lineno(0))
    if t[1] == "i32" or t[1] == "i8":
        op = "srem"
    elif t[1] == "float":
        op = "frem"

    code = p[1]["code"] + p[3]["code"]
    r1 = p[1]["reg"]
    r2 = p[3]["reg"]

    if p[1]["type"] != t:
        r1 = newReg()
        code += r1 + " = sext " + p[1]["type"][1] + " " + p[1]["reg"] + " to " + t[1] + "\n"
    if p[3]["type"] != t:
        r2 = newReg()
        code += r2 + " = sext " + p[3]["type"][1] + " " + p[3]["reg"] + " to " + t[1] + "\n"

    r3 = newReg()

    p[0] = {"reg" : r3,
            "code" : code + r3 + " = " + op + " " + t[1] + " " + r1 + ", " + r2 + "\n",
            "type" : t}
    pass

def p_multiplicative_expression_5(p):
    '''multiplicative_expression : multiplicative_expression LAND unary_expression'''
    t = getType(p[1]["type"], p[3]["type"], p.lineno(0))
    if t[1] == "i32" or t[1] == "i8":
        op = "mul"
    elif t[1] == "float":
        op = "fmul"

    code = p[1]["code"] + p[3]["code"]
    r1 = p[1]["reg"]
    r2 = p[3]["reg"]

    if p[1]["type"] != t:
        r1 = newReg()
        code +=  r1 + " = sext " + p[1]["type"][1] + " " + p[1]["reg"] + " to " + t[1] + "\n"
    if p[3]["type"] != t:
        r2 = newReg()
        code += r2 + " = sext " + p[3]["type"][1] + " " + p[3]["reg"] + " to " + t[1] + "\n"

    r3 = newReg()
    r4 = newReg()
    r5 = newReg()

    p[0] = {"reg" : r5,
            "code" : code + r3 + " = " + op + " " + t[1] + " " + r1 + ", " + r2 + "\n"
                   + r4 + " = icmp eq " + t[1] + " " + r3 + ", 0 \n"
                   + r5 + " = zext i1 " + r4 + " to i32\n",
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

    if t[1] == "i32" or t[1] == "i8":
        op = "add"
    elif t[1] == "float":
        op = "fadd"

    code = p[1]["code"] + p[3]["code"]
    r2 = p[1]["reg"]
    r3 = p[3]["reg"]

    if p[1]["type"] != t:
        r2 = newReg()
        code +=  r2 + " = sext " + p[1]["type"][1] + " " + p[1]["reg"] + " to " + t[1] + "\n"
    if p[3]["type"] != t:
        r3 = newReg()
        code += r3 + " = sext " + p[3]["type"][1] + " " + p[3]["reg"] + " to " + t[1] + "\n"

    p[0] = {"reg" : r1,
            "code" : code + r1 + " = " + op + " " + t[1] + " " + r2 + ", " + r3 + "\n",
            "type" : t}
    pass

def p_additive_expression_3(p):
    '''additive_expression : additive_expression MINUS multiplicative_expression'''
    t = getType(p[1]["type"], p[3]["type"], p.lineno(0))
    r1 = newReg()

    if t[1] == "i32" or t[1] == "i8":
        op = "sub"
    elif t[1] == "float":
        op = "fsub"

    code = p[1]["code"] + p[3]["code"]
    r2 = p[1]["reg"]
    r3 = p[3]["reg"]

    if p[1]["type"] != t:
        r2 = newReg()
        code +=  r2 + " = sext " + p[1]["type"][1] + " " + p[1]["reg"] + " to " + t[1] + "\n"
    if p[3]["type"] != t:
        r3 = newReg()
        code += r3 + " = sext " + p[3]["type"][1] + " " + p[3]["reg"] + " to " + t[1] + "\n"

    p[0] = {"reg" : r1,
            "code" : code + r1 + " = " + op + " " + t[1] + " " + r2 + ", " + r3 + "\n",
            "type" : t}
    pass

def p_additive_expression_4(p):
    '''additive_expression : additive_expression LOR multiplicative_expression'''
    t = getType(p[1]["type"], p[3]["type"], p.lineno(0))

    code = p[1]["code"] + p[3]["code"]
    r1 = p[1]["reg"]
    r2 = p[3]["reg"]

    if p[1]["type"] != t:
        r1 = newReg()
        code +=  r1 + " = sext " + p[1]["type"][1] + " " + p[1]["reg"] + " to " + t[1] + "\n"
    if p[3]["type"] != t:
        r2 = newReg()
        code += r2 + " = sext " + p[3]["type"][1] + " " + p[3]["reg"] + " to " + t[1] + "\n"

    r3 = newReg()
    r4 = newReg()
    r5 = newReg()
    if t[1] == "i32" or t[1] == "i8":
        op = "add"
    elif t[1] == "float":
        op = "fadd"

    p[0] = {"reg" : r1,
            "code" : p[1]["code"] + p[3]["code"]
                   + r3 + " = " + op + " " + t[1] + " " + r1 + ", " + r2 + "\n"
                   + r4 + " = icmp eq " + t[1] + " " + r3 + ", 0 \n"
                   + r5 + " = zext i1 " + r4 + " to i32\n",
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

    code = p[1]["code"] + p[3]["code"]
    r1 = p[1]["reg"]
    r2 = p[3]["reg"]

    if p[1]["type"] != t:
        r1 = newReg()
        code += r1 + " = sext " + p[1]["type"][1] + " " + p[1]["reg"] + " to " + t[1] + "\n"

    if p[3]["type"] != t:
        r2 = newReg()
        code += r2 + " = sext " + p[3]["type"][1] + " " + p[3]["reg"] + " to " + t[1] + "\n"

    r3 = newReg()
    r4 = newReg()
    p[0] = {"reg" : r4,
            "code" : code + r3 + " = icmp slt " + t[1] + " " + r1 + ", " + r2 + "\n"
                     + r4 + " = zext i1 " + r3 + " to i32\n",
            "type" : ["v", "i32"]}
    pass

def p_comparison_expression_3(p):
    '''comparison_expression : additive_expression GT additive_expression'''
    t = getType(p[1]["type"], p[3]["type"], p.lineno(0))

    code = p[1]["code"] + p[3]["code"]
    r1 = p[1]["reg"]
    r2 = p[3]["reg"]

    if p[1]["type"] != t:
        r1 = newReg()
        code += r1 + " = sext " + p[1]["type"][1] + " " + p[1]["reg"] + " to " + t[1] + "\n"

    if p[3]["type"] != t:
        r2 = newReg()
        code += r2 + " = sext " + p[3]["type"][1] + " " + p[3]["reg"] + " to " + t[1] + "\n"

    r3 = newReg()
    r4 = newReg()
    p[0] = {"reg" : r4,
            "code" : code + r3 + " = icmp sgt " + t[1] + " " + r1 + ", " + r2 + "\n"
                     + r4 + " = zext i1 " + r3 + " to i32\n",
            "type" : ["v", "i32"]}
    pass

def p_comparison_expression_4(p):
    '''comparison_expression : additive_expression LE additive_expression'''
    t = getType(p[1]["type"], p[3]["type"], p.lineno(0))

    code = p[1]["code"] + p[3]["code"]
    r1 = p[1]["reg"]
    r2 = p[3]["reg"]

    if p[1]["type"] != t:
        r1 = newReg()
        code += r1 + " = sext " + p[1]["type"][1] + " " + p[1]["reg"] + " to " + t[1] + "\n"

    if p[3]["type"] != t:
        r2 = newReg()
        code += r2 + " = sext " + p[3]["type"][1] + " " + p[3]["reg"] + " to " + t[1] + "\n"

    r3 = newReg()
    r4 = newReg()
    p[0] = {"reg" : r4,
            "code" : code + r3 + " = icmp sle " + t[1] + " " + r1 + ", " + r2 + "\n"
                     + r4 + " = zext i1 " + r3 + " to i32\n",
            "type" : ["v", "i32"]}
    pass

def p_comparison_expression_5(p):
    '''comparison_expression : additive_expression GE additive_expression'''
    t = getType(p[1]["type"], p[3]["type"], p.lineno(0))

    code = p[1]["code"] + p[3]["code"]
    r1 = p[1]["reg"]
    r2 = p[3]["reg"]

    if p[1]["type"] != t:
        r1 = newReg()
        code += r1 + " = sext " + p[1]["type"][1] + " " + p[1]["reg"] + " to " + t[1] + "\n"

    if p[3]["type"] != t:
        r2 = newReg()
        code += r2 + " = sext " + p[3]["type"][1] + " " + p[3]["reg"] + " to " + t[1] + "\n"

    r3 = newReg()
    r4 = newReg()
    p[0] = {"reg" : r4,
            "code" : code + r3 + " = icmp sge " + t[1] + " " + r1 + ", " + r2 + "\n"
                     + r4 + " = zext i1 " + r3 + " to i32\n",
            "type" : ["v", "i32"]}
    pass

def p_comparison_expression_6(p):
    '''comparison_expression : additive_expression EQ additive_expression'''
    t = getType(p[1]["type"], p[3]["type"], p.lineno(0))

    code = p[1]["code"] + p[3]["code"]
    r1 = p[1]["reg"]
    r2 = p[3]["reg"]

    if p[1]["type"] != t:
        r1 = newReg()
        code += r1 + " = sext " + p[1]["type"][1] + " " + p[1]["reg"] + " to " + t[1] + "\n"

    if p[3]["type"] != t:
        r2 = newReg()
        code += r2 + " = sext " + p[3]["type"][1] + " " + p[3]["reg"] + " to " + t[1] + "\n"

    r3 = newReg()
    r4 = newReg()
    p[0] = {"reg" : r4,
            "code" : code + r3 + " = icmp eq " + t[1] + " " + r1 + ", " + r2 + "\n"
                     + r4 + " = zext i1 " + r3 + " to i32\n",
            "type" : ["v", "i32"]}
    pass

def p_comparison_expression_7(p):
    '''comparison_expression : additive_expression NE additive_expression'''
    t = getType(p[1]["type"], p[3]["type"], p.lineno(0))

    code = p[1]["code"] + p[3]["code"]
    r1 = p[1]["reg"]
    r2 = p[3]["reg"]

    if p[1]["type"] != t:
        r1 = newReg()
        code += r1 + " = sext " + p[1]["type"][1] + " " + p[1]["reg"] + " to " + t[1] + "\n"

    if p[3]["type"] != t:
        r2 = newReg()
        code += r2 + " = sext " + p[3]["type"][1] + " " + p[3]["reg"] + " to " + t[1] + "\n"

    r3 = newReg()
    r4 = newReg()
    p[0] = {"reg" : r4,
            "code" : code + r3 + " = icmp ne " + t[1] + " " + r1 + ", " + r2 + "\n"
                     + r4 + " = zext i1 " + r3 + " to i32\n",
            "type" : ["v", "i32"]}
    pass

def p_expression_1(p):
    '''expression : unary_expression EQUALS comparison_expression'''
    if p[1]["type"] != p[3]["type"]:
        error(p.lineno(0), "Incompatible types in operation")
    if p[1]["type"][1] == "i32" or p[1]["type"][1] == "i8":
        op = "add"
    elif p[1]["type"][1] == "float":
        op = "fadd"
    r = newReg()
    p[0] = {"code" : p[1]["code"] + p[3]["code"]
                   + r + " = " + op + " " + p[1]["type"][1] + " " + p[3]["reg"] + ", 0\n"
                   + "store " + p[1]["type"][1] + " " + r + ", " + p[1]["type"][1] + "* " + p[1]["addr"] + "\n",
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
    p[0] = {"code" : p[1]["code"] + p[3]["code"]
                   + r1 + " = load " + p[1]["type"][1] + "* " + p[1]["addr"] + "\n"
                   + r2 + " = " + op + " " + p[1]["type"][1] + " " + r1 + ", " + p[3]["reg"] + "\n"
                   + "store " + p[1]["type"][1] + " " + r2 + ", " + p[1]["type"][1] + "* " + p[1]["addr"] + "\n",
            "reg" : r2,
            "addr" : p[1]["addr"],
            "type" : p[1]["type"]}
    pass

def p_expression_3(p):
    '''expression : unary_expression DIVEQUAL comparison_expression'''
    t = getType(p[1]["type"], p[3]["type"], p.lineno(0))
    if p[1]["type"] != t:
        error(p.lineno(0), "Incompatible types in operation")
        raise SyntaxError
    if t[1] == "i32" or t[1] == "i8":
        op = "sdiv"
    elif t[1] == "float":
        op = "fdiv"

    r1 = newReg()
    r2 = newReg()
    p[0] = {"code" : p[1]["code"] + p[3]["code"]
                   + r1 + " = load " + p[1]["type"][1] + "* " + p[1]["addr"] + "\n"
                   + r2 + " = " + op + " " + p[1]["type"][1] + " " + r1 + ", " + p[3]["reg"] + "\n"
                   + "store " + p[1]["type"][1] + " " + r2 + ", " + p[1]["type"][1] + "* " + p[1]["addr"] + "\n",
            "reg" : r2,
            "addr" : p[1]["addr"],
            "type" : p[1]["type"]}
    pass

def p_expression_4(p):
    '''expression : unary_expression MODEQUAL comparison_expression'''
    t = getType(p[1]["type"], p[3]["type"], p.lineno(0))
    if p[1]["type"] != t:
        error(p.lineno(0), "Incompatible types in operation")
        raise SyntaxError
    if t[1] == "i32" or t[1] == "i8":
        op = "srem"
    elif t[1] == "float":
        op = "frem"

    r1 = newReg()
    r2 = newReg()
    p[0] = {"code" : p[1]["code"] + p[3]["code"]
                   + r1 + " = load " + p[1]["type"][1] + "* " + p[1]["addr"] + "\n"
                   + r2 + " = " + op + " " + p[1]["type"][1] + " " + r1 + ", " + p[3]["reg"] + "\n"
                   + "store " + p[1]["type"][1] + " " + r2 + ", " + p[1]["type"][1] + "* " + p[1]["addr"] + "\n",
            "reg" : r2,
            "addr" : p[1]["addr"],
            "type" : p[1]["type"]}
    pass

def p_expression_5(p):
    '''expression : unary_expression PLUSEQUAL comparison_expression'''
    t = getType(p[1]["type"], p[3]["type"], p.lineno(0))
    if p[1]["type"] != t:
        error(p.lineno(0), "Incompatible types in operation")
        raise SyntaxError
    if t[1] == "i32" or t[1] == "i8":
        op = "add"
    elif t[1] == "float":
        op = "fadd"

    r1 = newReg()
    r2 = newReg()
    p[0] = {"code" : p[1]["code"] + p[3]["code"]
                   + r1 + " = load " + p[1]["type"][1] + "* " + p[1]["addr"] + "\n"
                   + r2 + " = " + op + " " + p[1]["type"][1] + " " + r1 + ", " + p[3]["reg"] + "\n"
                   + "store " + p[1]["type"][1] + " " + r2 + ", " + p[1]["type"][1] + "* " + p[1]["addr"] + "\n",
            "reg" : r2,
            "addr" : p[1]["addr"],
            "type" : p[1]["type"]}
    pass

def p_expression_6(p):
    '''expression : unary_expression MINUSEQUAL comparison_expression'''
    t = getType(p[1]["type"], p[3]["type"], p.lineno(0))
    if p[1]["type"] != t:
        error(p.lineno(0), "Incompatible types in operation")
        raise SyntaxError
    if t[1] == "i32" or t[1] == "i8":
        op = "sub"
    elif t[1] == "float":
        op = "fsub"

    r1 = newReg()
    r2 = newReg()
    p[0] = {"code" : p[1]["code"] + p[3]["code"]
                   + r1 + " = load " + p[1]["type"][1] + "* " + p[1]["addr"] + "\n"
                   + r2 + " = " + op + " " + p[1]["type"][1] + " " + r1 + ", " + p[3]["reg"] + "\n"
                   + "store " + p[1]["type"][1] + " " + r2 + ", " + p[1]["type"][1] + "* " + p[1]["addr"] + "\n",
            "reg" : r2,
            "addr" : p[1]["addr"],
            "type" : p[1]["type"]}
    pass

def p_expression_7(p):
    '''expression : comparison_expression'''
    p[0] = {"code" : p[1]["code"], "reg" : p[1]["reg"], "type" : p[1]["type"], "addr" : p[1]["addr"] if "addr" in p[1] else None}
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
    p[0] = {"code" : ""}
    pass
def p_expression_statement_2(p):
    '''expression_statement : expression SEMI'''
    p[0] = {"code" : p[1]["code"], "type" : p[1]["type"], "reg" : p[1]["reg"], "addr" : p[1]["addr"] if "addr" in p[1] else None}
    pass

def p_selection_statement_1(p):
    '''selection_statement : IF LPAREN expression RPAREN statement'''
    if_head = newLab()
    if_body = newLab()
    if_exit = newLab()
    r = newReg()
    p[0] = {"code" :  "br label %" + if_head + "\n"
                    + "\n" + if_head + ":\n"
                    + p[3]["code"] + "\n"
                    + r + " = icmp ne " + p[3]["type"][1] + " " + p[3]["reg"] + ", 0 \n"
                    + "br i1 " + r + ", label %" + if_body + ", label %" + if_exit + "\n"
                    + "\n" + if_body + ":\n"
                    + p[5]["code"]
                    + "br label %" + if_exit + "\n"
                    + "\n" + if_exit + ":\n"
           }
    pass

def p_selection_statement_2(p):
    '''selection_statement : IF LPAREN expression RPAREN statement ELSE statement'''
    if_head = newLab()
    if_yes = newLab()
    if_no = newLab()
    if_exit = newLab()
    r = newReg()
    p[0] = {"code" :  "br label %" + if_head + "\n"
                    + "\n" + if_head + ":\n"
                    + p[3]["code"] + "\n"
                    + r + " = icmp ne " + p[3]["type"][1] + " " + p[3]["reg"] + ", 0 \n"
                    + "br i1 " + r + ", label %" + if_yes + ", label %" + if_no + "\n"
                    + "\n" + if_yes + ":\n"
                    + p[5]["code"]
                    + "br label %" + if_exit + "\n"
                    + "\n" + if_no + ":\n"
                    + p[7]["code"]
                    + "br label %" + if_exit + "\n"
                    + "\n" + if_exit + ":\n"
           }
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
                     + r + " = icmp ne " + p[4]["type"][1] + " " + p[4]["reg"] + ", 0 \n"
                     + "br i1 " + r + ", label %" + loop_body + ", label %" + loop_exit + "\n"
                     + "\n" + loop_body + ": \n"
                     + p[7]["code"]
                     + "br label %" + loop_close + "\n"
                     + "\n" + loop_close + ": \n"
                     + p[5]["code"]
                     + "br label %" + loop_head + "\n"
                     + "\n" + loop_exit + ": \n"
           }
    pass

def p_iteration_statement_1(p):
    '''iteration_statement : WHILE LPAREN expression RPAREN statement'''
    loop_head = newLab()
    loop_body = newLab()
    loop_exit = newLab()
    r = newReg()
    p[0] = {"code" : "br label %" + loop_head + "\n"
                     + "\n" + loop_head + ": \n"
                     + p[3]["code"]
                     + r + " = icmp ne " + p[3]["type"][1] + " " + p[3]["reg"] + ", 0 \n"
                     + "br i1 " + r + ", label %" + loop_body + ", label %" + loop_exit + "\n"
                     + "\n" + loop_body + ": \n"
                     + p[5]["code"] + "\n"
                     + "br label %" + loop_head + "\n"
                     + "\n" + loop_exit + ": \n"
           }
    pass

def p_iteration_statement_2(p):
    '''iteration_statement : DO statement WHILE LPAREN expression RPAREN SEMI'''
    loop_body = newLab()
    loop_tail = newLab()
    loop_exit = newLab()
    r = newReg()
    p[0] = {"code" : "br label %" + loop_body + "\n"
                     + "\n" + loop_body + ": \n"
                     + p[2]["code"] + "\n"
                     + "br label %" + loop_tail + "\n"
                     + "\n" + loop_tail + ": \n"
                     + p[5]["code"] + "\n"
                     + r + " = icmp ne " + p[5]["type"][1] + " " + p[5]["reg"] + ", 0 \n"
                     + "br i1 " + r + ", label %" + loop_body + ", label %" + loop_exit + "\n"
                     + "\n" + loop_exit + ": \n"
           }
    pass

def p_jump_statement_1(p):
    '''jump_statement : RETURN SEMI'''
    p[0] = {"type" : ["v", "void"],
            "code" : "ret void"}
    pass

def p_jump_statement_2(p):
    '''jump_statement : RETURN expression SEMI'''
    p[0] = {"type" : p[2]["type"],
            "code" : p[2]["code"] + "ret " + p[2]["type"][1] + " " + p[2]["reg"]}
    pass

def p_error(p):
    if p:
        print("Syntax error at line " + str(p.lineno) + " : '" + p.value + "'")
    else:
        print("Syntax error at EOF")




# build parser

yacc.yacc(outputdir="build") #debug=0
