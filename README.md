# SPM (Serial-Parallel Multiplier): RTL-to-GDSII baseline

First end-to-end run of the open-source flow on my machine setup:
LibreLane (OpenLane 2) + SkyWater Sky130 PDK, run in GitHub Codespaces.

## Flow
RTL (Verilog) -> Yosys synthesis -> floorplan -> placement -> CTS ->
routing -> signoff (DRC, LVS, antenna) -> GDSII

## Results (nominal corner unless stated)
| Metric | Value |
|---|---|
| Target clock | 10 ns (100 MHz) |
| Worst setup slack | +3.59 ns (slow corner, ss_100C_1v60) |
| Worst hold slack | +0.253 ns (fast corner, ff_n40C_1v95) |
| Setup / hold violations | 0 / 0 |
| Die area | 10,367 um^2 |
| Core area | 7,214 um^2 |
| Std-cell area (excl. fill) | 4,547 um^2 |
| Total power (tt, 1.8 V) | ~1.48 mW |
| DRC (Magic + KLayout) | 0 |
| LVS errors | 0 |
| Antenna violations | 0 |

Timing was checked at three process corners (tt, ss, ff).

![Layout](spm_layout.png)

## Reproduce
    python3 -m venv .venv && source .venv/bin/activate
    pip install librelane
    python3 -m librelane --dockerized --pdk-root $HOME/.ciel designs/spm/config.yaml

## Notes
- Design comes from the LibreLane examples; this run validates the toolchain.
- Raw metrics: `metrics.csv`