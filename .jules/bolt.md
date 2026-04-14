## 2024-04-09 - [Streamlit Rerun Loop Allocations]
**Learning:** Streamlit reruns the entire script on every user interaction. Defining static lists inside rendering loops causes redundant memory allocations and garbage collection overhead on every rerun. For small literal collections in `in` checks (e.g. `c2 in ["A", "B"]`), CPython optimizes them better if they are tuples, avoiding list creation overhead entirely.
**Action:** Always hoist static arrays (like `YKSIKKO_OPTS_BASE`) outside of loops to reuse references, and prefer tuples over lists for static options or membership checks to minimize allocation overhead per rerun.
## 2024-04-14 - [Optimize safe_float with explicit type check]
**Learning:** `safe_float` was redundantly parsing inputs due to generic exception masking. `float()` naturally processes string inputs formatted securely, resolving string parsing inefficiencies. Removing repetitive `isinstance` overhead effectively reduces execution latency.
**Action:** Replace `isinstance` evaluations with explicit strict type evaluations (`type(v) is str`), avoid string casting numbers, and remove extraneous `.strip()` operations.
