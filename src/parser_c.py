# TODO: description

import lex_c


# global tables
# TODO: Do it ! just... DO IT !


def p_primary_expression(p):
    '''primary_expression : IDENTIFIER
                          | ICONST
                          | FCONST
                          | LPAREN expression RPAREN
                          | MAP LPAREN postfix_expression COMMA postfix_expression RPAREN
                          | REDUCE LPAREN postfix_expression COMMA postfix_expression RPAREN
                          | ID LPAREN RPAREN
                          | ID LPAREN argument_expression_list RPAREN
                          | ID PLUSPLUS
                          | ID MINUSMINUS'''
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
                                  | multiplicative_expression DIVIDE unary_expression'''
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
    ''' assignment_operator : EQUALS
                            | TIMESEQUAL
                            | DIVEQUAL
                            | MODEQUAL
                            | PLUSEQUAL
                            | MINUSEQUAL'''
    pass

def p_declaration(p):
    '''declaration : type_name declarator_list SEMI
                   | EXTERN type_name declarator_list SEMI'''
    pass

def p_declarator_list(p):
    '''declarator_list : declarator
                       | declarator_list COMMA declarator'''
    pass

def p_type_name(p):
    '''type_name : VOID
                 | INT
                 | FLOAT'''
    pass

def p_declarator(p):
    '''declarator : ID
                  | LPAREN declarator RPAREN
                  | declarator LBRACKET ICONST RBRACKET
                  | declarator LBRACKET RBRACKET
                  | declarator LPAREN parameter_list RPAREN
                  | declarator LPAREN RPAREN'''
    pass

def p_parameter_list(p):
    '''parameter_list : parameter_declaration
                      | parameter_list COMMA parameter_declaration'''
    pass

def p_parameter_declaration(p):
    '''parameter_declaration : type_name declarator'''
    pass

def p_statement(p):
    '''statement : compound_statement
                 | expression_statement
                 | selection_statement
                 | iteration_statement
                 | jump_statement'''
    pass

def p_compound_statement(p):
    '''compound_statement : LBRACE RBRACE
                          | LBRACE statement_list RBRACE
                          | LBRACE declaration_list statement_list RBRACE'''
    pass

def p_declaration_list(p):
    '''declaration_list : declaration
                        | declarator_list declaration'''
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

def p_program(p):
    '''program : external_declaration
               | program external_declaration'''
    pass

def p_external_declaration(p):
    '''external_declaration : function_definition
                            | declaration'''
    pass

def p_function_definition(p):
    '''function_definition : type_name declarator compound_statement'''
    pass

def p_error(p):
    if p:
        print("Syntax error at line " + p.lineno + " : '" + p.value + "'")
    else:
        print("Syntax error at EOF")




# build parser
import ply.yacc as yacc
yacc.yacc()



#yacc.yacc(outputdir='generated')

if __name__ == "__main__":
    import sysprog = file(sys.argv[1]).read()
    result = yacc.parse(prog)
    print result
