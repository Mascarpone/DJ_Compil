import sys, os

def getFiles(path, ext):
    return [f for f in os.listdir(path) if (os.path.isfile(os.path.join(path, f)) and f[-len(ext)-1:] == "."+ext)]

tst_recette = getFiles("./tst/tst_recette", "c")
tst_unit = getFiles("tst/tst_unit", "c")

def usage():
    sys.stderr.write("Usage: " + sys.argv[0] + " [ -unit | -recette | -all ]\n\n")
    sys.stderr.write("    -unit      Run unit tests\n")
    sys.stderr.write("    -recette   Run receipt tests\n")
    sys.stderr.write("    -all       Run all tests (unit + receipt)\n")
    sys.stderr.write("\n")
    sys.stderr.write("Usage: " + sys.argv[0] + " -test path/to/the/test/file.c\n")

def run_test(test_source_file, test_expected_output):
    pass


def run_unit():
    pass

def run_recette():
    pass


if __name__ == '__main__':
    if len(sys.argv) == 2:
        if sys.argv[1] == "-unit":
            run_unit()
        elif sys.argv[1] == "-recette":
            run_recette()
        elif sys.argv[1] == "-all":
            run_unit()
            run_recette()
        else:
            usage()
    elif len(sys.argv) == 3:
        pass
    else:
        usage()
