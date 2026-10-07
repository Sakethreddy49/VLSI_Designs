# Generic RTL / cocotb / OpenLane Makefile
# Generated from the generic-rtl-gds-project skill.

SHELL := /bin/bash

TOPLEVEL ?= handshake_dut
DESIGN_NAME ?= $(notdir $(abspath $(CURDIR)/..))
SIM ?= icarus
TOPLEVEL_LANG ?= verilog
COMPILE_ARGS += -g2012
SIM_ARGS ?=
COCOTB_TEST_MODULES ?= test_$(TOPLEVEL)
MODULE ?= $(COCOTB_TEST_MODULES)

TEST_DIR := $(abspath $(CURDIR))
PROJECT_DIR := $(abspath $(TEST_DIR)/..)
RTL_DIR := $(PROJECT_DIR)/src
RESULTS_DIR := $(PROJECT_DIR)/results
BUILD_DIR := $(TEST_DIR)/build
OPENLANE_CONFIG := $(PROJECT_DIR)/config.yaml

VERILOG_SOURCES := $(wildcard $(RTL_DIR)/*.v) $(wildcard $(RTL_DIR)/*.sv)
RTL_BINARY := $(BUILD_DIR)/$(TOPLEVEL).vvp

.PHONY: all sim rtl_compile rtl_run lint openlane clean_all clean_sim show_config check_sources

all: sim

sim: check_sources

check_sources:
	@set -e; \
	if [[ -z "$(strip $(VERILOG_SOURCES))" ]]; then \
		echo "ERROR: No RTL files found in $(RTL_DIR)"; exit 1; \
	fi; \
	echo "RTL sources:"; printf '  %s\n' $(VERILOG_SOURCES)

show_config:
	@echo "PROJECT_DIR: $(PROJECT_DIR)"
	@echo "RTL_DIR: $(RTL_DIR)"
	@echo "TOPLEVEL: $(TOPLEVEL)"
	@echo "DESIGN_NAME: $(DESIGN_NAME)"
	@echo "SIM: $(SIM)"
	@echo "COCOTB_TEST_MODULES: $(COCOTB_TEST_MODULES)"
	@printf 'RTL sources:\n'; printf '  %s\n' $(VERILOG_SOURCES)

rtl_compile: check_sources
	@mkdir -p "$(BUILD_DIR)"
	iverilog -g2012 -s "$(TOPLEVEL)" -o "$(RTL_BINARY)" $(COMPILE_ARGS) $(VERILOG_SOURCES)
	@echo "Compiled RTL: $(RTL_BINARY)"

rtl_run: rtl_compile
	vvp "$(RTL_BINARY)" $(SIM_ARGS)

lint: check_sources
	verilator --lint-only -Wall -Wno-fatal --top-module "$(TOPLEVEL)" $(VERILOG_SOURCES)

openlane:
	@set -e; \
	if [[ ! -f "$(OPENLANE_CONFIG)" ]]; then \
		echo "ERROR: OpenLane configuration not found: $(OPENLANE_CONFIG)"; exit 1; \
	fi; \
	cd "$(PROJECT_DIR)" && openlane --dockerized config.yaml

clean_all:
	@rm -rf "$(BUILD_DIR)" "$(TEST_DIR)/sim_build" "$(TEST_DIR)"/results \
		"$(TEST_DIR)"/dump.vcd "$(TEST_DIR)"/dump.fst "$(TEST_DIR)"/*.vvp
	@echo "Simulation-generated files removed."

clean_sim:
	@rm -rf "$(TEST_DIR)/sim_build" "$(TEST_DIR)"/results \
		"$(TEST_DIR)"/dump.vcd "$(TEST_DIR)"/dump.fst
	@echo "Cocotb simulation files removed."

include $(shell cocotb-config --makefiles)/Makefile.sim
