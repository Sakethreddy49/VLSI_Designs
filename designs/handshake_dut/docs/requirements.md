# Requirements

## Functional contract

- A transaction begins when `ready` is sampled high in `IDLE`.
- `valid` sampled high in the same cycle as `ready` produces a one-cycle `error_early` pulse.
- `valid` sampled high exactly one cycle after `ready` produces a one-cycle `handshake_ok` pulse.
- If `valid` is absent at the exact deadline, the DUT enters an error-wait state.
- A later `valid` produces a one-cycle `error_late` pulse.
- If no later `valid` arrives before the missing threshold, the DUT produces a one-cycle `error_missing` pulse.
- Outputs are cleared on every active clock unless the corresponding event is detected.

## Interface assumptions

| Signal | Direction | Width | Assumption |
|---|---:|---:|---|
| `clk` | input | 1 | 10 ns first-pass period for OpenLane configuration |
| `rst_n` | input | 1 | Asynchronous active-low reset |
| `ready` | input | 1 | Sampled synchronously on `clk` |
| `valid` | input | 1 | Sampled synchronously on `clk` |
| `handshake_ok` | output | 1 | One-cycle success pulse |
| `error_early` | output | 1 | One-cycle same-cycle violation pulse |
| `error_late` | output | 1 | One-cycle late-arrival pulse |
| `error_missing` | output | 1 | One-cycle missing-arrival pulse |

The source file did not specify a formal external timing constraint or a detailed missing threshold. The 10 ns clock and existing RTL counter behavior are therefore documented as demo assumptions, not signoff requirements.
