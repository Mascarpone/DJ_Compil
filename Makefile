LLC=clang
CFLAGS=-Wall

LIBS=$(wildcard ./src/lib/*)
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

$(BIN_DIR)/%: $(S_DIR)/%.ll
	mkdir -p $(dir $@)
	$(LLC) $(CFLAGS) -o $@ $< $(LIBS)

mrproper:
	rm -rf $(BUILD_DIR)
