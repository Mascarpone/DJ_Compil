# -*- coding: utf-8 -*-

# Compiler written with PLY for dj language
# by Florian LE VERN and Sylvain CASSIAU
# at ENSEIRB-Matmeca, Bordeaux, FRANCE
# november 2015

# This script reads a source file written in dj language and outputs the
# corresponding llvm internal representation which can be compiled by 'llc'
# to produce a .s file and then by 'gcc' to get a binary.


##############################   MAIN   ##############################

import sys
from tools import *
import scanner
import grammar
from ply import yacc as yacc
from grammar import cc

#if __name__ == "__main__":

if len(sys.argv) < 3:
    sys.stderr.write("usage: ...\n")
    sys.exit(1)

# read source file
f = open(sys.argv[1])
prog = f.read()
f.close()

# parse it
result = yacc.parse(prog)

# check errors
checkGenericErrors(cc, result)

# save result
if result is None:
    sys.stderr.write("Code production canceled\n")
else:
    print("\n        ===== CODE =====\n")
    print(result["code"])
    f = open(sys.argv[2], 'w')
    f.write(result["code"])
    f.close()
