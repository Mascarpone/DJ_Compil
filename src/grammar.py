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


# print lib
# printchar
cc.setType("printchar", FunctionType(ValueType.VOID, [ValueType.CHAR]))
cc.setAddr("printchar", "@printchar")
# printint
cc.setType("printint", FunctionType(ValueType.VOID, [ValueType.INT]))
cc.setAddr("printint", "@printint")
# printfloat
cc.setType("printfloat", FunctionType(ValueType.VOID, [ValueType.FLOAT]))
cc.setAddr("printfloat", "@printfloat")
# print
cc.setType("print", FunctionType(ValueType.VOID, [ArrayType(ValueType.CHAR)]))
cc.setAddr("print", "@print")


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
    '''external_declaration : declaration_statement'''
    p[0] = {"code" : p[1]["code"]}


#def p_external_declaration_3(p):
#    '''external_declaration : EXTERN declaration_statement'''
#    #FIXME : ici ce sont des variables globales externes. Ca se déclare sous la forme @G = external global i32
#    p[0] = {"code" : "; declare external global " + p[2]["code"]}


def p_external_declaration_4(p):
    '''external_declaration : EXTERN type_name function_declarator arguments_declaration SEMI'''
    global cc
    # function_declarator opens a new context that must be closed
    cc.close()
    # now back in global context:
    cc.setType(p[3]["name"], FunctionType(p[2]["type"], p[4]["type"]))
    cc.setAddr(p[3]["name"], "@"+p[3]["name"])
    p[0] = {"code" : "declare " + str(p[2]["type"]) + " @" + p[3]["name"] + "(" + p[4]["code"] + ")"}
    pass


def p_function_definition(p):
    '''function_definition : type_name function_declarator arguments_declaration compound_statement'''
    global cc
    if p[2]["name"] in reserved:
        error(p.lineno(2), "'"+p[2]["name"]+"' is a reseved keyword")
    if cc.exists(p[2]["name"]):
        warning(p.lineno(2), "You are redefining '"+p[2]["name"]+"'")
    cc.close()
    cc.setType(p[2]["name"], FunctionType(p[1]["type"], p[3]["type"]))
    cc.setAddr(p[2]["name"], "@"+p[2]["name"])

    # check return type
    for l, t in cc.getReturnTypes():
        if not t.equals(p[1]["type"]):
            error(l, "Incompatible return type. Expected '" + type2str(p[1]["type"]) + "' but got '" + type2str(t) + "'.")
    cc.resetReturnTypes()

    code = "define " + str(p[1]["type"]) + " @" + p[2]["name"] + "(" + p[3]["code"] + ") {\n"
    code += p[3]["init"]
    code += p[4]["code"]
    code += "\n}\n"
    p[0] = {"code" : code}


def p_function_declarator(p):
    '''function_declarator : ID'''
    global cc
    cc.new()
    cc.unactivateOpenNewContext()  # prevent compound statement from opening a new cc
    p[0] = {"name" : p[1]}


def p_arguments_declaration_1(p):
    '''arguments_declaration : LPAREN parameter_list RPAREN'''
    p[0] = {"type" : p[2]["type"],
            "code" : p[2]["code"],
            "init" : p[2]["init"]}


def p_arguments_declaration_2(p):
    '''arguments_declaration : LPAREN RPAREN'''
    p[0] = {"type" : [],
            "code" : "",
            "init" : ""}


def p_parameter_list_1(p):
    '''parameter_list : parameter_declaration'''
    p[0] = {"type" : [p[1]["type"]],
            "code" : p[1]["code"],
            "init" : p[1]["init"]}


def p_parameter_list_2(p):
    '''parameter_list : parameter_list COMMA parameter_declaration'''
    p[0] = {"type" : p[1]["type"] + [p[3]["type"]],
            "code" : p[1]["code"] + ", " + p[3]["code"],
            "init" : p[1]["init"] + p[3]["init"]}


def p_parameter_declaration(p):
    '''parameter_declaration : type_name ID'''
    global cc
    if p[2] in reserved:
        error(p.lineno(2), "'" + p[2] + "' is a reseved keyword")
    if cc.exists(p[2]):
        warning(p.lineno(2), "You are redefining '" + p[2] + "'")
    t = p[1]["type"]
    r = newReg()      # mutable var to use inside the function
    r_a = r + ".arg"  # argument of the function. not mutable
    init = r + " = alloca " + str(t) + "\n" # code to build the mutable argument
    cc.setType(p[2], p[1]["type"])
    cc.setAddr(p[2], r)
    if t.isValue() or t.isFunction():
        init += "store " + str(t) + " " + r_a + ", " + str(t) + "* " + r + "\n" # copy value
    elif t.isArray():
        reg_res = newReg()
        init += reg_res + " = load " + str(t) + "* " + r_a + "\n"
        init += "store " + str(t) + " " + reg_res + ", " + str(t) + "* " + r + "\n"
    p[0] = {"type" : t,
            "code" : str(t) + " " + r_a,
            "init" : init}


def p_type_name_1(p):
    '''type_name : VOID'''
    p[0] = {"type" : ValueType.VOID}


def p_type_name_2(p):
    '''type_name : CHAR'''
    p[0] = {"type" : ValueType.CHAR}


def p_type_name_3(p):
    '''type_name : INT'''
    p[0] = {"type" : ValueType.INT}


def p_type_name_4(p):
    '''type_name : FLOAT'''
    p[0] = {"type" : ValueType.FLOAT}


def p_type_name_5_1(p):
    '''type_name : type_name LBRACKET RBRACKET'''
    p[0] = {"type" : ArrayType(p[1]["type"]),
            "size" : None}


def p_type_name_5_2(p):
    '''type_name : type_name LBRACKET ICONST RBRACKET'''
    p[0] = {"type" : ArrayType(p[1]["type"]),
            "size" : int(p[3])}


def p_type_name_6(p):
    '''type_name : type_name LPAREN type_list RPAREN''' # int(int,char)
    p[0] = {"type" : FunctionType(p[1]["type"], p[3]["type"])}


def p_type_name_7(p):
    '''type_name : type_name LPAREN RPAREN''' # int()
    p[0] = {"type" : FunctionType(p[1]["type"], [])}


def p_type_list_1(p):
    '''type_list : type_name'''
    p[0] = {"type" : [p[1]["type"]]}


def p_type_list_2(p):
    '''type_list : type_list COMMA type_name'''
    p[0] = {"type" : p[1]["type"] + [p[3]["type"]]}


def p_compound_statement_begin(p):
    '''compound_statement_begin : LBRACE'''
    global cc
    if cc.compoundStatementOpenNewContext():
        cc.new()
    else:
        cc.activateOpenNewContext()
    p[0] = {}


def p_compound_statement_1(p):
    '''compound_statement : compound_statement_begin RBRACE'''
    p[0] = {"code" : ""}


def p_compound_statement_2(p):
    '''compound_statement : compound_statement_begin statement_list RBRACE'''
    p[0] = {"code" : p[2]["code"]}


def p_declaration_1(p):
    '''declaration_statement : type_name declarator_list SEMI'''
    global cc
    t = p[1]["type"]
    code = ""
    for d in p[2]: # d is a declarator
        if cc.exists(d["name"]):
            warning(p.lineno(2), "You are redefining " + d["name"]);
        reg = newReg()
        cc.setType(d["name"], t)
        cc.setAddr(d["name"], reg)
        code += reg + " = alloca " + str(t) + "\n"
        if d["code"] is not None:
            if not d["type"].equals(t):
                error(p.lineno(0), "Incompatible types in declaration. Expected '" + type2str(t) + "' but got '" + type2str(d["type"]) + "'.")
            code += d["code"]
            if t.isValue() or t.isFunction():
                code += "store " + str(d["type"]) + " " + d["reg"] + ", " + str(t) + "* " + reg + "\n"
            elif t.isArray():
                reg_res = newReg()
                code += reg_res + " = load " + str(d["type"]) + "* " + d["reg"] + "\n"
                code += "store " + str(d["type"]) + " " + reg_res + ", " + str(t) + "* " + reg + "\n"
                # copy size entry
                #reg_size_res_ptr = newReg()
                #code += reg_size_ptr + " = getelementptr " + str(d["type"]) + "* " + d["reg"] + ", i32 0, i32 0\n"
                #reg_size_res = newReg()
                #code += "load i32* " + reg_size_res_ptr + "\n"
                #reg_size_ptr = newReg()
                #code += reg_size_ptr + " = getelementptr " + str(t) + "* " + reg + ", i32 0, i32 0\n"
                #code += "store i32 " + reg_size + ", i32* " + reg_size_ptr + "\n"
                # copy buffer entry
        else:
            if t.isValue():
                code += "store " + str(t) + " 0, " + str(t) + "* " + reg + "\n"
            elif t.isFunction():
                code += "store " + str(t) + " null, " + str(t) + "* " + reg + "\n"
            elif t.isArray():
                # set size to 0
                reg_size_ptr = newReg()
                code += reg_size_ptr + " = getelementptr " + str(t) + "* " + reg + ", i32 0, i32 0\n"
                if p[1]["size"] is None:
                    code += "store i32 0, i32* " + reg_size_ptr + "\n"
                else:
                    code += "store i32 " + str(p[1]["size"]) + ", i32* " + reg_size_ptr + "\n"
                    allocated_buff = newReg()
                    code += allocated_buff + " = call i8* @malloc(i64 " + str(sizeof(t.getElementsType()) * p[1]["size"]) + ")\n"
                    cast_allocated = newReg()
                    code += cast_allocated + " = bitcast i8* " + allocated_buff + " to " + str(t.getElementsType()) + "*\n"
                    reg_buff_ptr = newReg()
                    code += reg_buff_ptr + " = getelementptr " + str(t) + "* " + reg + ", i32 0, i32 1\n"
                    code += "store " + str(t.getElementsType()) + "* " + cast_allocated + ", " + str(t.getElementsType()) + "** " + reg_buff_ptr + "\n"
    p[0] = {"code" : code,
            "reg" : reg,
            "type" : t}


def p_declarator_1(p):
    '''declarator : ID'''
    p[0] = {"name" : p[1],
            "reg" : None,
            "code" : None,
            "type" : None}


def p_declarator_2(p):
    '''declarator : ID EQUALS expression'''
    p[0] = {"name" : p[1],
            "reg" : p[3]["reg"],
            "code" : p[3]["code"],
            "type" : p[3]["type"]}


def p_primary_expression_id(p):
    '''primary_expression : ID'''
    global cc

    # get variable type and check if it has been defined
    t = cc.getType(p[1])
    if t is None:
        error(p.lineno(1), "The variable '" + p[1] + "' is not defined")

    # get register where the variable is stored
    r = cc.getAddr(p[1])
    if r is None:
        error(p.lineno(1), "The variable '" + p[1] + "' has not been initialized")

    p[0] = {"type" : t}
    # when its a value, generate load code
    if t.isValue() or (t.isFunction() and r[0] == "%"):
        p[0]["reg"] = newReg() # register for the value
        p[0]["code"] = p[0]["reg"] + " = load " + str(t) + "* " + r + "\n"
        p[0]["addr"] = r # keep address for affectation statement
    elif t.isFunction(): # starts with "@"
        p[0]["reg"] = r
        p[0]["code"] = ""
    elif t.isArray():
        p[0]["reg"] = r
        p[0]["addr"] = r
        p[0]["code"] = ""


def p_primary_expression_iconst(p):
    '''primary_expression : ICONST'''
    p[0] = {"type" : ValueType.INT, "code" : "", "reg" : p[1]}


def p_primary_expression_fconst(p):
    '''primary_expression : FCONST'''
    p[0] = {"type" : ValueType.FLOAT, "code" : "", "reg" : float_to_hex(float(p[1]))}


def p_primary_expression_sconst(p):
    '''primary_expression : SCONST'''
    global cc
    # escape string ad add it to data segment
    global_string, _, l = cc.addText(p.lineno(1), p[1])
    t = ArrayType(ValueType.CHAR)
    # get a register containing a char array
    tmp_r = newReg()
    code = tmp_r + " = alloca " + str(t) + "\n"
    r1 = newReg()
    code += r1 + " = load " + str(t) + "* " + tmp_r + "\n"
    # store the size of the string
    r2 = newReg()
    code += r2 + " = insertvalue " + str(t) + " " + r1 + ", i32 " + str(l) + ", 0\n"
    # allocate and store string buffer
    allocated_buff = newReg()
    code += allocated_buff + " = call i8* @malloc(i64 " + str(l + 1) + ")\n" # +1 to avoid allocating 0 bytes for empty strings #security
    reg = newReg()
    code += reg + " = insertvalue " + str(t) + " " + r2 + ", i8* " + allocated_buff + ", 1\n"
    reg_global_string_ptr = newReg()
    code += reg_global_string_ptr + " = getelementptr [" + str(l) + " x i8]* " + global_string + ", i64 0, i64 0\n"
    code += "call void @llvm.memcpy.p0i8.p0i8.i32(i8* " + allocated_buff + ", i8* " + reg_global_string_ptr + ", i32 " + str(l) + ", i32 1, i1 false)\n"

    # this is it
    p[0] = {"type" : t, "code" : code, "reg" : reg}


def p_primary_expression_cconst(p):
    '''primary_expression : CCONST'''
    p[0] = {"type" : ValueType.CHAR,
            "code" : ""}
    if sys.version_info[0] >= 3:
        p[0]["reg"] = str(ord(bytes(p[1][1:-1], "utf-8").decode("unicode_escape")))
    else:
        p[0]["reg"] = str(ord(p[1][1:-1].decode('string_escape')))


def p_primary_expression_paren_expr(p):
    '''primary_expression : LPAREN expression RPAREN'''
    p[0] = {"type" : p[2]["type"], "code" : p[2]["code"], "reg" : p[2]["reg"]}


def p_primary_expression_size(p):
    '''primary_expression : SIZE LPAREN postfix_expression RPAREN'''
    # int s = size(T[] a)
    if not p[3]["type"].isArray():
        error(p.lineno(3), "Argument of function 'size()' is expected to be an array. Got a '" + type2str(p[3]["type"]) + "'.")
    size_ptr = newReg()
    code = r + " = getelementptr " + str(p[3]["type"]) + "* " + p[3]["reg"] + ", i32 0, i32 0\n"
    size = newReg()
    code += size + " = load i32* " + size_ptr + "\n"
    p[0] = {"type" : ValueType.INT, "code" : code, "reg" : size}


def p_primary_expression_map(p):
    '''primary_expression : MAP LPAREN postfix_expression COMMA postfix_expression RPAREN'''
    # T1[] b = map(T1(*)(T2) f, T2[] a)
    if not p[3]["type"].isFunction():
        error(p.lineno(3), "First argument of function 'map()' is expected to be a function. Got a '" + type2str(p[3]["type"]) + "'.")
    if not p[5]["type"].isArray():
        error(p.lineno(5), "Second argument of function 'map()' is expected to be an array. Got a '" + type2str(p[5]["type"]) + "'.")
    if p[3]["type"].getArgsCount() != 1:
        error(p.lineno(5), "The function passed to 'map()' is not taking the expected number of arguments. Got '" + type2str(p[3]["type"].getArgsCount()) + "', expected 1.")
    if not p[3]["type"].getArgType(0).equals(p[5]["type"].getElementsType()):
        error(p.lineno(1), "Incompatible types in 'map()'. You are trying to match '" + type2str(p[3]["type"].getArgType(0)) + "' with '" + type2str(p[5]["type"].getElementsType()) + "'.")
    map_fct = getMapFunction(p[3]["type"].getArgType(0), p[3]["type"].getReturnType())
    p[0] = {"code" : p[3]["code"] + p[5]["code"]}
    if p[3]["type"].getReturnType().equals(ValueType.VOID):
        p[0]["type"] = ValueType.VOID
        p[0]["reg"]  = None
        p[0]["code"] += "call void " + map_fct + "(" + str(p[3]["type"]) + " " + p[3]["reg"] + ", " + str(p[5]["type"]) + " " + p[5]["reg"] + ")\n"
    else:
        p[0]["type"] = ArrayType(p[3]["type"].getReturnType())
        p[0]["reg"]  = newReg()
        p[0]["code"] += p[0]["reg"] + " = call " + str(p[3]["type"].getReturnType()) + " " + map_fct + "(" + str(p[3]["type"]) + " " + p[3]["reg"] + ", " + str(p[5]["type"]) + " " + p[5]["reg"] + ")\n"
    p[0] = {"type" : ArrayType(p[3]["type"].getReturnType()), "code" : code, "reg" : r}


def p_primary_expression_reduce(p):
    # T b = reduce(T(*)(T,T) f, T[] a)
    '''primary_expression : REDUCE LPAREN postfix_expression COMMA postfix_expression RPAREN'''
    if not p[3]["type"].isFunction():
        error(p.lineno(3), "First argument of function 'reduce()' is expected to be a function. Got a '" + type2str(p[3]["type"]) + "'.")
    if not p[5]["type"].isArray():
        error(p.lineno(5), "Second argument of function 'reduce()' is expected to be an array. Got a '" + type2str(p[5]["type"]) + "'.")
    if p[3]["type"].getArgsCount() != 2:
        error(p.lineno(5), "The function passed to 'reduce()' is not taking the expected number of arguments. Got '" + str(p[3]["type"].getArgsCount()) + "', expected 2.")
    if not p[3]["type"].getReturnType().equals(p[5]["type"].getElementsType()) or not p[3]["type"].getArgType(0).equals(p[5]["type"].getElementsType()) or not p[3]["type"].getArgType(1).equals(p[5]["type"].getElementsType()):
        error(p.lineno(1), "Incompatible types in 'reduce()'. You are trying to match '" + type2str(p[3]["type"].getReturnType()) + "', '" + type2str(p[3]["type"].getArgType(0)) + "', '" + type2str(p[3]["type"].getArgType(1)) + "' with '" + type2str(p[5]["type"].getElementsType()) + "'.")
    if p[3]["type"].getReturnType().equals(ValueType.VOID):
        error(p.lineno(1), "You are trying to use 'void' as a type in reduce() function.")


    reduce_fct = getMapFunction(p[3]["type"].getReturnType())
    p[0] = {"code" : p[3]["code"] + p[5]["code"]}
    if p[3]["type"].getReturnType().equals(ValueType.VOID):
        p[0]["type"] = ValueType.VOID
        p[0]["reg"]  = None
        p[0]["code"] += "call void " + map_fct + "(" + str(p[3]["type"]) + " " + p[3]["reg"] + ", " + str(p[5]["type"]) + " " + p[5]["reg"] + ")\n"
    else:
        p[0]["type"] = ArrayType(p[3]["type"].getReturnType())
        p[0]["reg"]  = newReg()
        p[0]["code"] += p[0]["reg"] + " = call " + str(p[3]["type"].getReturnType()) + " " + map_fct + "(" + str(p[3]["type"]) + " " + p[3]["reg"] + ", " + str(p[5]["type"]) + " " + p[5]["reg"] + ")\n"
    p[0] = {"type" : ArrayType(p[3]["type"].getReturnType()), "code" : code, "reg" : r}


    # TODO forbid void types
    p[0] = {"type" : p[3]["type"].getReturnType(), "code" : "; primary_expression_reduce", "reg" : "registre"}


def p_primary_expression_id_paren(p):
    '''primary_expression : ID LPAREN RPAREN'''
    global cc
    if not cc.exists(p[1]):
        error(p.lineno(1), "The expression '" + p[1] + "' is not defined")
    t = cc.getType(p[1])
    if not t.isFunction():
        error(p.lineno(1), "You are trying to call '" + p[1] + "', which is not a function.")
    if t.getArgsCount() != 0:
        error(p.lineno(1), "Invalid number of arguments. Got " + str(t.getArgsCount()) + " but expected 0.")

    # call function
    code = "call " + str(t.getReturnType()) + " " + cc.getAddr(p[1]) + "()\n"
    r = None
    # store result if any
    if not t.getReturnType().equals(ValueType.VOID):
        r = newReg()
        code = r + " = " + code

        # if returning an array, allocate result to use it as a pointer
        #if t.getReturnType().isArray():
        #    tmp_r = r
        #    r = newReg()
        #    code += r + " = alloca " + t.getReturnType() + "\n"
        #    code += "store " + str(t.getReturnType()) + " " + tmp_r + ", " + t.getReturnType() + "* " + r + "\n"

    p[0] = {"type" : t.getReturnType(), "code" : code, "reg" : r}


def p_primary_expression_id_paren_args(p):
    '''primary_expression : ID LPAREN argument_expression_list RPAREN'''
    global cc
    if not cc.exists(p[1]):
        error(p.lineno(1), "The expression '" + p[1] + "' is not defined")
    t = cc.getType(p[1])
    if not t.isFunction():
        error(p.lineno(1), "You are trying to call '" + p[1] + "', which is not a function.")
    if t.getArgsCount() != len(p[3]["type"]):
        error(p.lineno(1), "Invalid number of arguments. Got " + str(len(p[3]["type"])) + " but expected " + str(t.getArgsCount()) + ".")
    if cc.getAddr(p[1]) is None:
        error(p.lineno(1), "'" + p[1] + "' has not been initialized.")

    # Check arguments types
    code = []
    for arg_reg, arg_t, expected_t in zip(p[3]["reg"], p[3]["type"], t.a):
        if not arg_t.equals(expected_t):
            error(p.lineno(0), "Incompatible types in function call. Got '" + type2str(arg_t) + "' but expected '" + type2str(expected_t) + "'.")
        code.append(str(arg_t) + " " + arg_reg)
    code = "call " + str(t.getReturnType()) + " " + cc.getAddr(p[1]) + "(" + ", ".join(code) + ")\n"

    r = None
    # store result if any
    if not t.getReturnType().equals(ValueType.VOID):
        r = newReg()
        code = r + " = " + code

        # if returning an array, allocate result to use it as a pointer
        #if t.getReturnType().isArray():
        #    tmp_r = r
        #    r = newReg()
        #    code += r + " = alloca " + t.getReturnType() + "\n"
        #    code += "store " + str(t.getReturnType()) + " " + tmp_r + ", " + t.getReturnType() + "* " + r + "\n"

    p[0] = {"type" : t.getReturnType(), "code" : p[3]["code"] + code, "reg" : r}


def p_primary_expression_id_plusplus(p):
    '''primary_expression : ID PLUSPLUS'''
    global cc
    if not cc.exists(p[1]):
        error(p.lineno(1), "The expression '" + p[1] + "' is not defined")
    t = cc.getType(p[1])
    if t.equals(ValueType.INT) or t.equals(ValueType.CHAR):
        op = "add"
    elif t.equals(ValueType.FLOAT):
        op = "fadd"
    else:
        error(p.lineno(0), "Trying to increment something not a value.")

    r = cc.getAddr(p[1])
    r1 = newReg()
    r2 = newReg()
    p[0] = {"type" : t,
            "reg" : r,
            "code" :   r1 + " = load " + str(t) + "* " + r + "\n"
                     + r2 + " = " + op + " " + str(t) + " " + r1 + ", 1 \n"
                     + "store " + str(t) + " " + r2 + ", " + str(t) + "* " + r + "\n"}


def p_primary_expression_id_minusminus(p):
    '''primary_expression : ID MINUSMINUS'''
    global cc
    if not cc.exists(p[1]):
        error(p.lineno(1), "The expression '" + p[1] + "' is not defined")
    t = cc.getType(p[1])
    if t.equals(ValueType.INT) or t.equals(ValueType.CHAR):
        op = "sub"
    elif t.equals(ValueType.FLOAT):
        op = "fsub"
    else:
        error(p.lineno(0), "Trying to decrement something not a value.")

    r = cc.getAddr(p[1])
    r1 = newReg()
    r2 = newReg()
    p[0] = {"type" : t,
            "reg" : r,
            "code" :   r1 + " = load " + str(t) + "* " + r + "\n"
                     + r2 + " = " + op + " " + str(t) + " " + r1 + ", 1 \n"
                     + "store " + str(t) + " " + r2 + ", " + str(t) + "* " + r + "\n"}


def p_postfix_expression_1(p):
    '''postfix_expression : primary_expression'''
    p[0] = {"type" : p[1]["type"],
            "reg" : p[1]["reg"],
            "code" : p[1]["code"]}
    if "addr" in p[1]:
        p[0]["addr"] = p[1]["addr"]


def p_postfix_expression_2(p):
    '''postfix_expression : postfix_expression LBRACKET expression RBRACKET'''
    if not p[1]["type"].isArray():
        error(p.lineno(0), "Trying to access to an element of something which is not an array.")
    if not p[3]["type"].equals(ValueType.INT):
        error(p.lineno(0), "The index of an array must be an integer.")

    code = p[1]["code"] + p[3]["code"]
    buff_ptr = newReg()
    code += buff_ptr + " = getelementptr " + str(p[1]["type"]) + "* " + p[1]["addr"] + ", i32 0, i32 1\n"
    buff = newReg()
    code += buff + " = load " + str(p[1]["type"].getElementsType()) + "** " + buff_ptr + "\n"
    elt_ptr = newReg()
    code += elt_ptr + " = getelementptr " + str(p[1]["type"].getElementsType()) + "* " + buff + ", i32 " + p[3]["reg"] + "\n"
    elt = newReg()
    code += elt + " = load " + str(p[1]["type"].getElementsType()) + "* " + elt_ptr + "\n"

    p[0] = {"type" : p[1]["type"].getElementsType(),
            "reg" : elt,
            "addr" : elt_ptr,
            "code" : code}


def p_argument_expression_list_1(p):
    '''argument_expression_list : expression'''
    p[0] = {"code" : p[1]["code"], "type" : [p[1]["type"]], "reg" : [p[1]["reg"]]}


def p_argument_expression_list_2(p):
    '''argument_expression_list : argument_expression_list COMMA expression'''
    p[0] = {"code" : p[1]["code"] + p[3]["code"], "type" : p[1]["type"] + [p[3]["type"]], "reg" : p[1]["reg"] + [p[3]["reg"]]}


# Operations

def convert(reg, tbefore, tafter, newreg, lineno):
    '''Returns the code to convert in llvm the value in reg from type tbefore to tafter and store it in newreg'''
    if tbefore.equals(ValueType.CHAR) and tafter.equals(ValueType.INT):
        op = "sext"
    elif (tbefore.equals(ValueType.INT) or tbefore.equals(ValueType.CHAR)) and tafter.equals(ValueType.FLOAT):
        op = "sitofp"
    else :
        error(lineno, "Invalid implicit conversion.")

    return newreg + " = " + op + " " + str(tbefore) + " " + reg + " to " + str(tafter) + "\n"

operation_intchar = {"*" : "mul", "/" : "sdiv", "%" : "srem", "+" : "add", "-" : "sub", "<" : "icmp slt", ">" : "icmp sgt", "<=" : "icmp sle", ">=" : "icmp sge", "==" : "icmp eq", "!=" : "icmp ne"}
operation_float = {"*" : "fmul", "/" : "fdiv", "%" : "frem", "+" : "fadd", "-" : "fsub", "<" : "fcmp olt", ">" : "fcmp ogt", "<=" : "fcmp ole", ">=" : "fcmp oge", "==" : "fcmp oeq", "!=" : "fcmp one"}
def operation(operation, op1, op2, lineno):
    '''Generates the code and the registers necessary to implement the operation between op1 and op2'''
    t = op1["type"].getOpResultType(op2["type"])
    if t is None or not t.isValue():
        error(lineno, "Incompatible types in operation " + operation + ". Got " + type2str(op1["type"]) + " and " + type2str(op2["type"]))

    if t.equals(ValueType.INT) or t.equals(ValueType.CHAR):
        operation_llvm = operation_intchar[operation]
    if t.equals(ValueType.FLOAT):
        operation_llvm = operation_float[operation]

    code = op1["code"] + op2["code"]

    r1 = op1["reg"]
    r2 = op2["reg"]
    if not op1["type"].equals(t):
        r1 = newReg()
        code += convert(op1["reg"], op1["type"], t, r1, lineno)
    if not op2["type"].equals(t):
        r2 = newReg()
        code += convert(op2["reg"], op2["type"], t, r2, lineno)

    r3 = newReg()
    code += r3 + " = " + operation_llvm + " " + str(t) + " " + r1 + ", " + r2 + "\n"

    return {"reg" : r3, "code" : code, "type" : t} #WARNING: type t is false if the operation is a comparison (then it is a i1)

#Unary Expressions

def unaryOperation(operation, x, n):
    t = x["type"]
    if t.equals(ValueType.INT) or t.equals(ValueType.CHAR):
        operation_llvm = operation_intchar[operation]
    if t.equals(ValueType.FLOAT):
        operation_llvm = operation_float[operation]

    code = x["code"]
    r = newReg()
    code += r + " = " + operation_llvm + " " + str(t) + " " + x["reg"] + ", " + str(n) + "\n"
    return {"reg" : r, "code" : code, "type" : t}

def p_unary_expression_1(p):
    '''unary_expression : postfix_expression'''
    p[0] = {"code" : p[1]["code"], "type" : p[1]["type"], "reg" : p[1]["reg"]}
    if "addr" in p[1]:
        p[0]["addr"] = p[1]["addr"]
    pass

def p_unary_expression_2(p):
    '''unary_expression : PLUSPLUS unary_expression'''
    p[0] = unaryOperation('+', p[2], 1)
    p[0]["code"] += "store " + str(p[0]["type"]) + " " + p[0]["reg"] + ", " + str(p[0]["type"]) + "* " + p[2]["addr"] + "\n"
    p[0]["addr"] = p[2]["addr"]

def p_unary_expression_3(p):
    '''unary_expression : MINUSMINUS unary_expression'''
    p[0] = unaryOperation('-', p[2], 1)
    p[0]["code"] += "store " + str(p[0]["type"]) + " " + p[0]["reg"] + ", " + str(p[0]["type"]) + "* " + p[2]["addr"] + "\n"
    p[0]["addr"] = p[2]["addr"]

def p_unary_expression_4(p):
    '''unary_expression : MINUS unary_expression'''
    p[0] = unaryOperation('*', p[2], -1)

def p_unary_expression_5(p):
    '''unary_expression : LNOT unary_expression'''
    p[0] = unaryOperation('==', p[2], 0)
    r = newReg()
    p[0]["code"] += r + " = zext i1 " + p[0]["reg"] + " to i32\n"
    p[0]["reg"] = r
    p[0]["type"] = ValueType.INT

#Comparison Expressions

def comparisonOperation(comparison, op1, op2, lineno):
    '''Generates the code and the registers necessary to implement the comparison between op1 and op2'''
    resi1 = operation(comparison, op1, op2, lineno)
    booli32 = newReg()
    return {"reg"  : booli32,
            "code" : resi1["code"]
                     + booli32 + " = zext i1 " + resi1["reg"] + " to i32\n",
            "type" : ValueType.INT}

def p_comparison_expression_1(p):
    '''comparison_expression : additive_expression'''
    p[0] = {"reg" : p[1]["reg"], "code" : p[1]["code"], "type" : p[1]["type"]}

def p_comparison_expression_2(p):
    '''comparison_expression : additive_expression LT additive_expression'''
    p[0] = comparisonOperation(p[2], p[1], p[3], p.lineno(0))

def p_comparison_expression_3(p):
    '''comparison_expression : additive_expression GT additive_expression'''
    p[0] = comparisonOperation(p[2], p[1], p[3], p.lineno(0))

def p_comparison_expression_4(p):
    '''comparison_expression : additive_expression LE additive_expression'''
    p[0] = comparisonOperation(p[2], p[1], p[3], p.lineno(0))

def p_comparison_expression_5(p):
    '''comparison_expression : additive_expression GE additive_expression'''
    p[0] = comparisonOperation(p[2], p[1], p[3], p.lineno(0))

def p_comparison_expression_6(p):
    '''comparison_expression : additive_expression EQ additive_expression'''
    p[0] = comparisonOperation(p[2], p[1], p[3], p.lineno(0))

def p_comparison_expression_7(p):
    '''comparison_expression : additive_expression NE additive_expression'''
    p[0] = comparisonOperation(p[2], p[1], p[3], p.lineno(0))

#Additive Expression

def p_additive_expression_1(p):
    '''additive_expression : multiplicative_expression'''
    p[0] = {"reg" : p[1]["reg"], "code" : p[1]["code"], "type" : p[1]["type"]}

def p_additive_expression_2(p):
    '''additive_expression : additive_expression PLUS multiplicative_expression'''
    p[0] = operation(p[2], p[1], p[3], p.lineno(0))

def p_additive_expression_3(p):
    '''additive_expression : additive_expression MINUS multiplicative_expression'''
    p[0] = operation(p[2], p[1], p[3], p.lineno(0))

def p_additive_expression_4(p):
    '''additive_expression : additive_expression LOR multiplicative_expression'''
    add = operation("+", p[1], p[3], p.lineno(0))
    booli1_cmpto0 = newReg()
    booli32_cmpto0 = newReg()

    p[0] = {"reg"  : booli32_cmpto0,
            "code" : add["code"]
                   + booli1_cmpto0 + " = icmp ne " + str(add["type"]) + " " + add["reg"] + ", 0 \n"
                   + booli32_cmpto0 + " = zext i1 " + booli1_cmpto0 + " to i32\n",
            "type" : ValueType.INT}

#Multiplicative Expression

def p_multiplicative_expression_1(p):
    '''multiplicative_expression : unary_expression'''
    p[0] = {"reg" : p[1]["reg"], "code" : p[1]["code"], "type" : p[1]["type"]}

def p_multiplicative_expression_2(p):
    '''multiplicative_expression : multiplicative_expression TIMES unary_expression'''
    p[0] = operation(p[2], p[1], p[3], p.lineno(0))

def p_multiplicative_expression_3(p):
    '''multiplicative_expression : multiplicative_expression DIVIDE unary_expression'''
    p[0] = operation(p[2], p[1], p[3], p.lineno(0))

def p_multiplicative_expression_4(p):
    '''multiplicative_expression : multiplicative_expression MOD unary_expression'''
    p[0] = operation(p[2], p[1], p[3], p.lineno(0))

def p_multiplicative_expression_5(p):
    '''multiplicative_expression : multiplicative_expression LAND unary_expression'''
    mul = operation("*", p[1], p[3], p.lineno(0))
    booli1_cmpto0 = newReg()
    booli32_cmpto0 = newReg()

    p[0] = {"reg"  : booli32_cmpto0,
            "code" : mul["code"]
                   + booli1_cmpto0 + " = icmp ne " + str(mul["type"]) + " " + mul["reg"] + ", 0 \n"
                   + booli32_cmpto0 + " = zext i1 " + booli1_cmpto0 + " to i32\n",
            "type" : ValueType.INT}

#Affectation Expression

def expressionOperation(operation, op1, op2, lineno):
    '''Generates the code and the registers necessary to implement the affectation operation between op1 and op2'''
    t = op1["type"].getOpResultType(op2["type"])
    if t is None or not t.isValue() or not op1["type"].equals(t):
        error(lineno, "Incompatible types in operation " + operation + ". Got " + type2str(op1["type"]) + " and " + type2str(op2["type"]))

    if t.equals(ValueType.INT) or t.equals(ValueType.CHAR):
        operation_llvm = operation_intchar[operation]
    if t.equals(ValueType.FLOAT):
        operation_llvm = operation_float[operation]

    code = op1["code"] + op2["code"]

    op1load = newReg()
    code += op1load + " = load " + str(op1["type"]) + "* " + op1["addr"] + "\n"

    r2 = op2["reg"]
    if not op2["type"].equals(t):
        r2 = newReg()
        code += convert(op2["reg"], op2["type"], t, r2, lineno)

    result = newReg()
    code += result + " = " + operation_llvm + " " + str(t) + " " + op1load + ", " + r2 + "\n"
    code += "store " + str(op1["type"]) + " " + result + ", " + str(op1["type"]) + "* " + op1["addr"] + "\n"

    return {"type" : t,
            "reg"  : result,
            "addr" : op1["addr"],
            "code" : code
            }

def p_expression_1(p):
    '''expression : comparison_expression'''
    p[0] = {"code" : p[1]["code"], "reg" : p[1]["reg"], "type" : p[1]["type"], "addr" : p[1]["addr"] if "addr" in p[1] else None}
    pass

def p_expression_2(p):
    '''expression : unary_expression EQUALS comparison_expression'''
    if p[1]["type"].isArray() and p[3]["type"].isArray():
        if not p[1]["type"].getElementsType().equals(p[3]["type"].getElementsType()):
            error(p.lineno(0), "Affecting arrays of different types.")
        code = p[1]["code"] + p[3]["code"]
        comp_val = newReg()
        code += comp_val + " = load " + str(p[3]["type"]) + "* " + p[3]["reg"] + "\n"
        code += "store " + str(p[3]["type"]) + " " + comp_val + ", " + str(p[3]["type"]) + "* " + p[1]["reg"] + "\n"
        p[0] = {"code" : code, "reg" : p[3]["reg"], "type" : p[3]["type"]}
    else:
        r3 = p[3]["reg"]
        code = p[1]["code"] + p[3]["code"]
        if not p[3]["type"].equals(p[1]["type"]):
            r3 = newReg()
            code += convert(p[3]["reg"], p[3]["type"], p[1]["type"], r3, p.lineno(0)) #checks types
        code += "store " + str(p[1]["type"]) + " " + r3 + ", " + str(p[1]["type"]) + "* " + p[1]["addr"] + "\n"
        p[0] = {"code" : code,
                "reg" : r3,
                "addr" : p[1]["addr"],
                "type" : p[1]["type"]}
    pass

def p_expression_3(p):
    '''expression : unary_expression TIMESEQUAL comparison_expression'''
    p[0] = expressionOperation("*", p[1], p[3], p.lineno(0))

def p_expression_4(p):
    '''expression : unary_expression DIVEQUAL comparison_expression'''
    p[0] = expressionOperation("/", p[1], p[3], p.lineno(0))

def p_expression_5(p):
    '''expression : unary_expression MODEQUAL comparison_expression'''
    p[0] = expressionOperation("%", p[1], p[3], p.lineno(0))

def p_expression_6(p):
    '''expression : unary_expression PLUSEQUAL comparison_expression'''
    p[0] = expressionOperation("+", p[1], p[3], p.lineno(0))

def p_expression_7(p):
    '''expression : unary_expression MINUSEQUAL comparison_expression'''
    p[0] = expressionoperation("-", p[1], p[3], p.lineno(0))

#Declarator

def p_declarator_list_1(p):
    '''declarator_list : declarator'''
    p[0] = [p[1]]

def p_declarator_list_2(p):
    '''declarator_list : declarator_list COMMA declarator'''
    p[0] = p[1] + [p[3]]

#Statement

def p_statement(p):
    '''statement : compound_statement
                 | expression_statement
                 | selection_statement
                 | iteration_statement
                 | jump_statement
                 | declaration_statement'''
    p[0] = {"code" : p[1]["code"]}

def p_statement_list_1(p):
    '''statement_list : statement'''
    p[0] = {"code" : p[1]["code"]}

def p_statement_list_2(p):
    '''statement_list : statement_list statement'''
    p[0] = {"code" : p[1]["code"] + p[2]["code"]}

def p_expression_statement_1(p):
    '''expression_statement : SEMI'''
    p[0] = {"code" : ""}

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
                    + r + " = icmp ne " + str(p[3]["type"]) + " " + p[3]["reg"] + ", 0 \n"
                    + "br i1 " + r + ", label %" + if_body + ", label %" + if_exit + "\n"
                    + "\n" + if_body + ":\n"
                    + p[5]["code"]
                    + "br label %" + if_exit + "\n"
                    + "\n" + if_exit + ":\n"
           }

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
                    + r + " = icmp ne " + str(p[3]["type"]) + " " + p[3]["reg"] + ", 0 \n"
                    + "br i1 " + r + ", label %" + if_yes + ", label %" + if_no + "\n"
                    + "\n" + if_yes + ":\n"
                    + p[5]["code"]
                    + "br label %" + if_exit + "\n"
                    + "\n" + if_no + ":\n"
                    + p[7]["code"]
                    + "br label %" + if_exit + "\n"
                    + "\n" + if_exit + ":\n"
           }

def p_selection_statement_3(p):
    '''selection_statement : for_keyword LPAREN expression_statement expression_statement expression RPAREN statement'''
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
                     + r + " = icmp ne " + str(p[4]["type"]) + " " + p[4]["reg"] + ", 0 \n"
                     + "br i1 " + r + ", label %" + loop_body + ", label %" + loop_exit + "\n"
                     + "\n" + loop_body + ": \n"
                     + p[7]["code"]
                     + "br label %" + loop_close + "\n"
                     + "\n" + loop_close + ": \n"
                     + p[5]["code"]
                     + "br label %" + loop_head + "\n"
                     + "\n" + loop_exit + ": \n"
           }

def p_for_keyword(p):
    '''for_keyword : FOR'''
    global cc, compound_statement_open_new_cc
    cc.new()
    compound_statement_open_new_cc = False
    p[0] = {}

def p_iteration_statement_1(p):
    '''iteration_statement : WHILE LPAREN expression RPAREN statement'''
    loop_head = newLab()
    loop_body = newLab()
    loop_exit = newLab()
    r = newReg()
    p[0] = {"code" : "br label %" + loop_head + "\n"
                     + "\n" + loop_head + ": \n"
                     + p[3]["code"]
                     + r + " = icmp ne " + str(p[3]["type"]) + " " + p[3]["reg"] + ", 0 \n"
                     + "br i1 " + r + ", label %" + loop_body + ", label %" + loop_exit + "\n"
                     + "\n" + loop_body + ": \n"
                     + p[5]["code"] + "\n"
                     + "br label %" + loop_head + "\n"
                     + "\n" + loop_exit + ": \n"
           }

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
                     + r + " = icmp ne " + str(p[5]["type"]) + " " + p[5]["reg"] + ", 0 \n"
                     + "br i1 " + r + ", label %" + loop_body + ", label %" + loop_exit + "\n"
                     + "\n" + loop_exit + ": \n"
           }


def p_jump_statement_1(p):
    '''jump_statement : RETURN SEMI'''
    global cc
    cc.addReturnType((p.lineno(0), ValueType.VOID))
    p[0] = {"code" : "ret void"}


def p_jump_statement_2(p):
    '''jump_statement : RETURN expression SEMI'''
    global cc
    cc.addReturnType((p.lineno(0), p[2]["type"]))
    p[0] = {"code" : p[2]["code"] + "ret " + str(p[2]["type"]) + " " + p[2]["reg"]}


# If no rules have been found
def p_error(p):
    if p:
        print("Syntax error at line " + str(p.lineno) + " : '" + p.value + "'")
    else:
        print("Syntax error at EOF")




# build parser

yacc.yacc(outputdir="build") #debug=0
