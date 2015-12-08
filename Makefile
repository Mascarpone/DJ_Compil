CC=gcc
LLC=llc
CFLAGS=-Wall

PARSER=./src/DJ_compil.py
BUILD_DIR=./build
C_DIR=./tst
LL_DIR=$(BUILD_DIR)/ll
S_DIR=$(BUILD_DIR)/s

TST_UNIT_C=$(wildcard ./tst/tst_unit/*.c)
TST_RECETTE_C=$(wildcard ./tst/tst_recette/*.c)

.PHONY: all tst_recette tst_unit mrproper

all: tst_recette tst_unit

tst_recette:

tst_unit:


$(LL_DIR)/%.ll: $(C_DIR)/%.c $(PARSER)
	mkdir -p $(dir $@)
	cd $(BUILD_DIR)
	python $(PARSER) $< $@

mrproper:
	rm -rf $(BUILD_DIR)
