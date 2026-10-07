# handshake_dut

A reusable RTL-to-GDSII demo generated from a single supplied SystemVerilog design file. The DUT checks whether `valid` arrives exactly one clock after `ready` and emits success or diagnostic pulses for early, late, and missing responses.

## Project structure

```text
handshake_dut/
├── README.md
├── config.yaml
├── docs/
│   ├── architecture.md
│   ├── requirements.md
│   └── verification_plan.md
├── results/
├── src/
│   └── handshake_dut.sv
└── test/
    ├── Makefile
    └── test_handshake_dut.py
```

## Top-level interface

The top module is `handshake_dut`. It uses an asynchronous active-low reset (`rst_n`) and a demo clock constraint of 10 ns (100 MHz). See `docs/requirements.md` for the assumptions made because the original design file did not include a separate specification.

## RTL validation

From the repository root:

```bash
iverilog -g2012 -s handshake_dut -o /tmp/handshake_dut.vvp \
  designs/handshake_dut/src/handshake_dut.sv
verilator --lint-only -Wall \
  designs/handshake_dut/src/handshake_dut.sv
```

If cocotb is installed:

```bash
cd designs/handshake_dut/test
make clean_all
make
```

## Physical design

After simulation and lint pass, and with OpenLane plus a compatible PDK available:

```bash
cd designs/handshake_dut
openlane --dockerized config.yaml
```

No GDSII result is claimed by this demo until that command is run successfully.
