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


if len(sys.argv) < 3:
    sys.stderr.write("Usage: "+sys.argv[0]+" <input_file> <output_file>\n")
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
    sys.stderr.write(bcolors.FAIL + "Code production canceled\n" + bcolors.ENDC)
else:
    print("\n        ===== CODE =====\n")
    print(cc.generateText())
    print(cc.generateArrayType())
    print(result["code"])
    with open(sys.argv[2], "w") as f:
        f.write("declare i8* @malloc(i64)")
        seg = cc.generateText()
        if seg != "":
            f.write("; Constant text\n")
            f.write(seg)
        at = cc.generateArrayType()
        if at != "":
            f.write("; Array types\n")
            f.write(at)
        f.write("\n; Main segment\n")
        f.write(result["code"])
