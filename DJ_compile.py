#!/usr/bin/python

import sys, os, subprocess, random
from subprocess import Popen, PIPE

dj_source_ext = "dj"
lib_files = ["src/lib/print.ll", "src/lib/print.c"]

def usage():
    sys.stderr.write("Usage: " + sys.argv[0] + " [ -o output ] input1.[ll|c] input2.[ll|c]\n\n")
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
    else:
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
                    exit(1)
                else:
                    print input_files[i] + " -> " + tmp_ll_out[-1] + " : OK"
            elif not getFileExt(input_files[i]) in [dj_source_ext, "c", "ll"]:
                sys.stderr.write("DJ_compile: ." + getFileExt(input_files[i]) + " files are not supported\n")
                exit(1)
        print "Looking for LLVM compiler..."
        cc = chooseLlvmCompiler()
        if cc == 0:
            sys.stderr.write("Neither llc nor clang was found on your system. Install them first.")
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
                    else:
                        print input_files[i] + " -> " + tmp_s_out[-1] + " : OK"
            code, out, err = runCommand("gcc -o " + output_file + " " + " ".join(tmp_s_out) + " " + " ".join([f for f in input_files if not getFileExt(f) in [dj_source_ext,"ll"]]))
            if code != 0:
                sys.stderr.write("Something went wrong...\n")
                print out
                #sys.stderr.write(err+"\n")
            else:
                map(os.remove, tmp_s_out)
                print "Compilation OK. Try to run " + output_file
        elif cc == 2: # clang
            print "Found clang"
            cmd = "clang -o " + output_file + " " + " ".join(tmp_ll_out) + " " + " ".join([f for f in input_files if not getFileExt(f) in [dj_source_ext]])
            print cmd
            exit_code, out, err = runCommand(cmd)
            if exit_code == 0:
                map(os.remove, tmp_ll_out)
                print "Compilation OK. Try to run " + output_file
            else:
                sys.stderr.write("Something went wrong...\n")
                print out
                #sys.stderr.write(err)
