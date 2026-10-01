SIM ?= icarus
TOPLEVEL_LANG = verilog
VERILOG_SOURCES = $(PWD)/../src/uart_tx.v
TOPLEVEL = uart_tx
# both names, because cocotb 1.x and 2.x differ
MODULE = test_uart_tx
COCOTB_TEST_MODULES = test_uart_tx
COMPILE_ARGS += -Puart_tx.CLKS_PER_BIT=8

include $(shell cocotb-config --makefiles)/Makefile.sim