# cocotb + Icarus Verilog simulation of matrix_mult
SIM ?= icarus
TOPLEVEL_LANG ?= verilog
VERILOG_SOURCES = $(PWD)/matrix_mult.sv
COMPILE_ARGS += -g2012
COCOTB_TOPLEVEL = matrix_mult
TOPLEVEL = matrix_mult
COCOTB_TEST_MODULES = test_matrix_mult
MODULE = test_matrix_mult

include $(shell cocotb-config --makefiles)/Makefile.sim
