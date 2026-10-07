# Verification Plan

## Simulation tests

The cocotb suite covers the externally visible protocol outcomes:

1. Same-cycle `ready` and `valid` -> `error_early`.
2. `valid` exactly one cycle after `ready` -> `handshake_ok`.
3. `valid` after the exact deadline -> `error_late`.
4. No `valid` after `ready` -> `error_missing`.

Each test applies asynchronous reset before stimulus and checks that event outputs are one-cycle pulses.

## Static checks

- Icarus Verilog/SystemVerilog compilation with the DUT as top-level.
- Verilator lint with warnings enabled.
- OpenLane should only be run after the RTL checks pass and a compatible PDK/toolchain is available.

## Follow-up coverage

For production signoff, add assertions or a formal model for reset during each state, back-to-back `ready` events, `valid` coincident with a new `ready` after recovery, counter rollover, and illegal state recovery.
