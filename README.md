# DJ_Compil

The DJ_Compil project is an attempt to create a compiler for a C-like programming language supporting automatic vectorization and parallelization for operations over arrays, like map() and reduce(). Actually, these functionalities are not included in v1.0, and `dj` is just our cool own-made and very limited programming language. :-)

Version 1.0 has been developed by `Mascarpone` and `pyvain` in November and December of 2015 as a compiling project assignment at ENSEIRB-Matmeca Engineering School, Bordeaux, France.


# Tools

This compiler uses `PLY` which is an implementation of `lex` and `yacc` parsing tools for Python. See http://www.dabeaz.com/ply/

It translates `dj` code in `llvm` programming language (http://llvm.org/docs/LangRef.html), and compiles it with `llc` and `gcc` or `clang`.


# How to use DJ_Compil

The main file of our compiler is `DJ_compile.py`, located at the root of the repository. To compile one or multiple files written in `dj` programming language, such as an example of the `tst` directory, and link them with other `.ll` or `.c` files, use it as follow :

`python DJ_compile.py [-o binary_output] source_file.<dj|c|ll> ...`

The `-o binary_output` argument is optional. If it is not given, the produced binary will be named `a.out`. You can edit the first line of `DJ_compile.py` and grant it execution rights to use it as a runnable.

This script uses `src/DJ_compil.py`, which converts files written in `dj` programming language to `llvm` thanks to `src/scanner.py` and `src/grammar.py`. These two files contain respectively the scanner and the parser for `dj` programming language. They are the core of this project. They go along with `src/tools.py` which is a collection of functions used to model manipulated data in the scanner and the parser.  The script then automatically add display libraries located in `src/lib`, and looks for `llc` and `gcc` compilers or for `clang` to compile and link all files in order to obtain a binary.


# Documentation

The code is partly documented in source files, and we should probably have written more indications to allow people to understand what we tried to do. However, `doc/COMPILATION_RP1.pdf` and `doc/COMPILATION_RP2.pdf` contain precious informations about what is supported in `dj` programming language and how to use `dj` compiler, but they are written in French. We will probably translate it in English if this project is to be continued.
