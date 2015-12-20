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
try:
    f = open(sys.argv[1])
    prog = f.read()
    f.close()
except IOError as e:
    sys.stderr.write("No such file: " + sys.argv[1] + "\n")
    exit(1)


# parse it
result = yacc.parse(prog)

# check errors
checkGenericErrors(cc, result)

# save result
if result is None:
    sys.stderr.write(bcolors.FAIL + "Code production canceled\n" + bcolors.ENDC)
else:
    with open(sys.argv[2], "w") as f:
        f.write("declare i8* @malloc(i64)\n")
        f.write("declare void @llvm.memcpy.p0i8.p0i8.i32(i8*, i8*, i32, i32, i1)\n")
        f.write("declare void @printchar(i8)\n")
        f.write("declare void @printint(i32)\n")
        f.write("declare void @printfloat(float)\n")
        f.write("declare void @print({i32,i8*})\n")
        seg = cc.generateText()
        if seg != "":
            f.write("\n; Global strings\n")
            f.write(seg)
        map_code = cc.generateMapFunctions()
        if map_code != "":
            f.write("\n; map() functions\n")
            f.write(map_code)
        reduce_code = cc.generateReduceFunctions()
        if reduce_code != "":
            f.write("\n; reduce() functions\n")
            f.write(reduce_code)
        f.write("\n; Main segment\n")
        f.write(result["code"])
