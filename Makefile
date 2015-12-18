CC=gcc
LLC=llc
CFLAGS=-Wall

LIBS=./src/lib/print.c # $(wildcard ./src/lib/*)
PARSER=./src/DJ_compil.py
BUILD_DIR=./build
C_DIR=./tst
LL_DIR=$(BUILD_DIR)/ll
S_DIR=$(BUILD_DIR)/s
BIN_DIR=$(BUILD_DIR)/bin

TST_UNIT_C=$(wildcard ./tst/tst_unit/*.c)
TST_RECETTE_C=$(wildcard ./tst/tst_recette/*.c)

.PHONY: all tst_recette tst_unit mrproper

all: tst_recette tst_unit

tst_recette:

tst_unit:


$(LL_DIR)/%.ll: $(C_DIR)/%.c $(PARSER)
	mkdir -p $(dir $@)
	python $(PARSER) $< $@

$(S_DIR)/%.s: $(LL_DIR)/%.ll $(PARSER)
	mkdir -p $(dir $@)
	llc -o $@ $<

$(BIN_DIR)/%: $(S_DIR)/%.s
	mkdir -p $(dir $@)
	$(CC) $(CFLAGS) -o $@ $< $(LIBS)

mrproper:
	rm -rf $(BUILD_DIR)
