## 2024-04-09 - [Streamlit Rerun Loop Allocations]
**Learning:** Streamlit reruns the entire script on every user interaction. Defining static lists inside rendering loops causes redundant memory allocations and garbage collection overhead on every rerun. For small literal collections in `in` checks (e.g. `c2 in ["A", "B"]`), CPython optimizes them better if they are tuples, avoiding list creation overhead entirely.
**Action:** Always hoist static arrays (like `YKSIKKO_OPTS_BASE`) outside of loops to reuse references, and prefer tuples over lists for static options or membership checks to minimize allocation overhead per rerun.
## 2024-05-01 - [Generator vs Explicit OR Overhead]
**Learning:** In Python, using `any(x in t for x in ["A", "B", "C"])` introduces significant overhead due to generator instantiation. For small, fixed-size checks, an explicit condition like `"A" in t or "B" in t or "C" in t` is ~4-5x faster.
**Action:** Replace `any()` with explicit `or` conditions for simple, finite substring checks in hot paths to avoid generator overhead.

## 2024-05-01 - [Cold Path Micro-optimizations]
**Learning:** Optimizing a string unit check (e.g., `yksikko == "mg/m2" or "mg/m2" in yksikko`) is functionally faster but represents a micro-optimization in a cold path, violating the directive against meaningless micro-optimizations.
**Action:** Avoid exact equality short-circuits for substring matches unless proven to be in a frequently executed hot path where the substring search dominates execution time.
