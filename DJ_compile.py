#!/usr/bin/python

import sys, os, subprocess, random
from subprocess import Popen, PIPE

dj_source_ext = "dj"
lib_files = ["src/lib/print.ll", "src/lib/print.c"]

def usage():
    sys.stderr.write("Compiler for DJ coding language. v1.0\n")
    sys.stderr.write("Copyright (c) 2015 Mascarpone, Pyvain - MIT Licence\n")
    sys.stderr.write("\n")
    sys.stderr.write("Usage: " + sys.argv[0] + " [ -o output ] input1.[dj|ll|c] input2.[dj|ll|c]\n")
    sys.stderr.write("    -o output      Specify an output file. Default is a.out\n")
    sys.stderr.write("\n")


def runCommand(cmd):
    process = Popen(cmd.split(), stdout=PIPE)
    (output, err) = process.communicate()
    exit_code = process.wait()
    return (exit_code, output, err) # exit code, stdout, stderr


def chooseLlvmCompiler():
    code, _, _ = runCommand("which llc")
    if code == 0:
        return 1
    else:
        code, _, _ = runCommand("which clang")
        if code == 0:
            return 2
        else:
            return 0


def getFileExt(fileName):
    l = fileName.split(".")
    if len(l) < 2:
        return ""
    else:
        return l[-1]

tmp_file_count = 0
def generateTmpFileName(ext = "tmp"):
    global tmp_file_count
    while os.path.isfile("/tmp/djcompil" + str(tmp_file_count) + "." + ext):
        tmp_file_count += 1
    return "/tmp/djcompil" + str(tmp_file_count) + "." + ext


if __name__ == '__main__':
    if len(sys.argv) < 2:
        usage()
        exit(1)
    else:
        code, out, err = runCommand("which gcc")
        if code != 0:
            sys.stderr(sys.argv[0] + ": Couldn't find GCC. Install it first.\n")
            exit(1)
        output_file = "a.out"
        index_input_file = 1
        if sys.argv[1] == "-o" and len(sys.argv) > 3:
            output_file = sys.argv[2]
            index_input_file = 3
        input_files = sys.argv[index_input_file:] + lib_files
        # compile DJ source files
        tmp_ll_out = []
        for i in range(len(input_files)):
            if getFileExt(input_files[i]) == dj_source_ext:
                # compile it with DJ_compile
                tmp_ll_out.append(generateTmpFileName("ll"))
                code,out,err = runCommand("python ./src/DJ_compil.py " + input_files[i] + " " + tmp_ll_out[-1])
                if code != 0:
                    sys.stderr.write(input_files[i] + " -> " + tmp_ll_out[-1] + " : FAILED\n")
                    print out
                    #sys.stderr.write(err+"\n")
                    exit(2)
                else:
                    print out
                    print input_files[i] + " -> " + tmp_ll_out[-1] + " : OK"
            elif not getFileExt(input_files[i]) in [dj_source_ext, "c", "ll"]:
                sys.stderr.write(sys.argv[0] + ": ." + getFileExt(input_files[i]) + " files are not supported\n")
                exit(1)
        print "Looking for LLVM compiler..."
        cc = chooseLlvmCompiler()
        if cc == 0:
            sys.stderr.write(sys.argv[0] + ": Neither llc nor clang was found on your system. Install one of them first.")
            exit(1)
        elif cc == 1: # llc
            print "Found llc"
            tmp_s_out = []
            for i in range(len(tmp_ll_out)):
                tmp_s_out.append(generateTmpFileName("s"))
                code,out,err = runCommand("llc -o " + tmp_s_out[-1] + " " + tmp_ll_out[i])
                if code != 0:
                    sys.stderr.write(tmp_ll_out[i] + " -> " + tmp_s_out[-1] + " : FAILED\n")
                    print out
                    #sys.stderr.write(err+"\n")
                    exit(3)
                else:
                    os.remove(tmp_ll_out[i])
                    print tmp_ll_out[i] + " -> " + tmp_s_out[-1] + " : OK"
            for i in range(len(input_files)):
                if getFileExt(input_files[i]) == "ll":
                    tmp_s_out.append(generateTmpFileName("s"))
                    code,out,err = runCommand("llc -o " + tmp_s_out[-1] + " " + input_files[i])
                    if code != 0:
                        sys.stderr.write(input_files[i] + " -> " + tmp_s_out[-1] + " : FAILED\n")
                        print out
                        #sys.stderr.write(err+"\n")
                        exit(3)
                    else:
                        print input_files[i] + " -> " + tmp_s_out[-1] + " : OK"
            code, out, err = runCommand("gcc -o " + output_file + " " + " ".join(tmp_s_out) + " " + " ".join([f for f in input_files if not getFileExt(f) in [dj_source_ext,"ll"]]))
            if code != 0:
                sys.stderr.write(sys.argv[0] + ": Something went wrong...\n")
                print out
                #sys.stderr.write(err+"\n")
                exit(4)
            else:
                map(os.remove, tmp_s_out)
                print "Compilation OK. Try to run " + output_file
        elif cc == 2: # clang
            print "Found clang"
            exit_code, out, err = runCommand("clang -o " + output_file + " " + " ".join(tmp_ll_out) + " " + " ".join([f for f in input_files if not getFileExt(f) in [dj_source_ext]]))
            if exit_code == 0:
                map(os.remove, tmp_ll_out)
                print "Compilation OK. Try to run " + output_file
            else:
                sys.stderr.write(sys.argv[0] + ": Something went wrong...\n")
                print out
                #sys.stderr.write(err)
                exit(4)
