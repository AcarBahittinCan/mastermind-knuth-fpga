# Mastermind Solver: Knuth's Algorithm in Python and Verilog

Implementation of **Knuth's five-guess algorithm** for Mastermind (4 digits, 6 colours, 1296 codes), first as a Python reference model and then as **synthesizable Verilog**, implemented on a **Xilinx Artix-7 FPGA**. The hardware solver cracks any secret code in **at most 5 guesses** using the minimax strategy.

> EE468 Digital Design project, Özyeğin University

The repo follows the full software → hardware flow:

1. **Python reference model**, a readable golden model of Knuth's algorithm
2. **Numba-accelerated generalisations** to a much larger search space (5 digits × 10 colours = 100,000 codes)
3. **RTL implementation**: FSM + score unit + candidate filter + minimax unit, verified against the Python model

---

## Repository structure

```
rtl/      Verilog design (scoreUnit, candidate_filter, minimax_unit, mastermind_top)
sim/      Testbenches (scoreUnit_tb, mastermind_top_tb)
python/   Reference model and accelerated variants
```

## Python models

| File | Description |
|---|---|
| `python/knuth_reference.py` | Classic Knuth algorithm (4 digits, colours 1–6). Plain Python golden model used to verify the RTL. Includes `garantiyi_dogrula()`, which runs all 1296 secrets and checks the ≤5 guess guarantee |
| `python/knuth_numba_5x10.py` | Generalised to 5 digits × 10 colours (100,000 codes). Numba JIT kernels, minimax with **early-exit pruning**, and random sampling of the guess space when candidates > 3000 |
| `python/knuth_entropy_5x10.py` | Same search space, but chooses guesses by **maximum entropy** of the feedback distribution instead of minimax, using multiprocessing |

```bash
pip install numpy numba
python python/knuth_reference.py      # example games + full 1296-code verification (slow, pure Python)
python python/knuth_numba_5x10.py     # 100 random 5x10 games
```

---

## Hardware design

### `scoreUnit.v`
Combinational module that computes the Mastermind score between two codes.

- **Inputs:** `code1 [19:0]`, `code2 [19:0]` — two codes, 4 bits per digit
- **Outputs:** `plus [2:0]` — exact matches (right digit, right position), `minus [2:0]` — right digit, wrong position
- **Parameter:** `CODE_LEN` (default 5, set to 4 for this design)
- **Algorithm:** Two-pass approach with used flags to prevent double-counting

### `candidate_filter.v`
Sequential module that eliminates candidates inconsistent with the last guess and score.

- **Inputs:** `clk`, `rst`, `enable`, `guess [15:0]`, `plus_in [2:0]`, `minus_in [2:0]`
- **Output:** `done`
- **Operation:** Iterates over all 1296 candidate flags; clears any code whose score against the last guess does not match the received feedback
- **Latency:** 1296 clock cycles per filter pass

### `minimax_unit.v`
Sequential module that finds the next best guess using Knuth's minimax strategy.

- **Inputs:** `clk`, `rst`, `enable`, `candidates [1295:0]`
- **Outputs:** `best_guess [15:0]`, `done`
- **Algorithm:** For each of 1296 candidate guesses, computes the worst-case remaining candidate count across all possible score groups; selects the guess that minimizes this worst case
- **Tiebreaker:** Prefers codes that are still candidates; then numerically smaller code
- **Latency:** ~1296 × 1296 clock cycles (worst case)

### `mastermind_top.v`
Top-level FSM that orchestrates all submodules.

- **Inputs:** `clk`, `rst`, `secret [15:0]`
- **Outputs:** `guess [15:0]`, `plus_out [2:0]`, `minus_out [2:0]`, `attempts [3:0]`, `done`
- **First guess:** Hardcoded to `(1,1,2,2)` (0x1122) — Knuth's optimal opening move with worst-case 256 remaining candidates
- **FSM states:** IDLE → SCORE → CHECK → FILTER → MINIMAX → DONE

---

## Code encoding

Each 4-digit code is packed into 16 bits, 4 bits per digit:

```
code[15:12] = digit 0  (MSB)
code[11:8]  = digit 1
code[7:4]   = digit 2
code[3:0]   = digit 3  (LSB)
```

Digits range from 1 to 6. Total of 6^4 = 1296 valid codes.

---

## Simulation

Testbenches are in `sim/`. Run them in Vivado (or any Verilog simulator) with `rtl/` as the source.

| Secret | Hex | Attempts |
|---|---|---|
| 1,1,2,2 | `0x1122` | 1 |
| 6,6,6,6 | `0x6666` | 3 |
| 3,6,1,4 | `0x3614` | 4 |

All results match the Python reference model.

## Synthesis & implementation

**Target Device:** Xilinx Artix-7 — xc7a12ticsg325-1L  
**Tool:** Vivado 2025.2  

### Timing

| Parameter              | Value        |
|------------------------|--------------|
| Clock Constraint       | None defined |
| Critical Path Delay    | 49.446 ns    |
| Estimated f_max        | ~20.2 MHz    |
| WNS                    | inf (unconstrained) |

The critical path runs through the `minimax_unit` — specifically the
worst-case comparison chain across 25 group counters into `best_worst_case`
and `best_guess` registers (52 logic levels, 24 CARRY4 + LUT chain).

### Resource Utilization

| Resource        | Used  | Available | Utilization |
|-----------------|-------|-----------|-------------|
| Slice LUTs      | 3186  | 8000      | 39.83%      |
| Slice Registers | 1675  | 16000     | 10.47%      |
| Bonded IOBs     | 45    | 150       | 30.00%      |
| Block RAM       | 0     | 20        | 0.00%       |
| DSPs            | 0     | 40        | 0.00%       |
| BUFGCTRL        | 1     | 32        | 3.13%       |
| F7 Muxes        | 512   | 7300      | 7.01%       |
| F8 Muxes        | 242   | 3650      | 6.63%       |

The 1296-bit candidate flag array in `candidate_filter` is implemented
entirely in flip-flops (FDPE), accounting for the majority of register usage.
No Block RAM is used. The large LUT count comes from the minimax comparison
tree and the combinational `idx_to_code` function instantiated in multiple modules.

---

### Possible improvements

- Add a clock constraint and **pipeline the minimax comparison chain** (52 logic levels) to raise f_max
- Move the 1296-bit candidate array into **Block RAM** to free up flip-flops
- Evaluate several guesses in parallel in `minimax_unit` to cut the ~1296² cycle latency

## Tools

- Vivado 2025.2, target `xc7a12ticsg325-1L` (Artix-7)
- Python 3, NumPy, Numba

## Author

**Bahittin Can Acar**
