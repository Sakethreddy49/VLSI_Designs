# Architecture

`handshake_dut` is a compact finite-state protocol monitor.

```text
                 valid same cycle
        +--------------------------------+
        |                                v
     IDLE --ready/no valid--> WAIT_VAL  error_early -> IDLE
       ^                          |
       |                          | valid on next edge
       |                          v
       |                       handshake_ok -> IDLE
       |
       +<------------------- ERR <--- no valid at deadline
                              |  \
                    valid ----+   +---- counter threshold -> error_missing
                         error_late
```

## State responsibilities

- **IDLE**: Wait for `ready`; reject same-cycle `valid` as early.
- **WAIT_VAL**: Check `valid` on the next sampled clock edge.
- **ERR**: Wait for a late `valid` or assert missing after the counter threshold.
- **DONE**: Reserved encoding in the original state type; the current implementation returns to `IDLE` if reached.

The implementation uses one sequential block with an asynchronous active-low reset, matching the supplied source. The counter is 4 bits and is treated as an unsigned integer (`UQ4.0` in fixed-point notation, although it is used as a cycle count rather than a fractional value).
