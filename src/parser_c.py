# TODO: description

import ply.yacc as yacc
from lex_c import tokens



def p_expression_num(p):
    'expression : NUMBER'
    p[0] = p[1]

def p_error(p):
    print "Syntax error in line %d " % p.lineno
    yacc.errok()


yacc.yacc(outputdir='generated')

if __name__ == "__main__":
    import sysprog = file(sys.argv[1]).read()
    result = yacc.parse(prog)
    print result
