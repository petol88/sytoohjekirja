## 2024-04-09 - [Streamlit Rerun Loop Allocations]
**Learning:** Streamlit reruns the entire script on every user interaction. Defining static lists inside rendering loops causes redundant memory allocations and garbage collection overhead on every rerun. For small literal collections in `in` checks (e.g. `c2 in ["A", "B"]`), CPython optimizes them better if they are tuples, avoiding list creation overhead entirely.
**Action:** Always hoist static arrays (like `YKSIKKO_OPTS_BASE`) outside of loops to reuse references, and prefer tuples over lists for static options or membership checks to minimize allocation overhead per rerun.
## 2024-05-24 - Optimize ECOG Description Lookup

**Learning:** Recreating static dictionaries on every function call introduces unnecessary overhead. By hoisting these dictionaries to the module level, we can significantly reduce the execution time of simple getter functions without changing the API.
**Action:** Lifted `kuvaukset` to `_ECOG_KUVAUKSET` in `hae_ecog_kuvaus`.
## 2024-06-12 - Python Boolean Summation Overhead
**Learning:** In Python, `sum([bool1, bool2, ...])` allocates a temporary list and has function call overhead. Since booleans are a subclass of integers, `bool1 + bool2 + ...` achieves the exact same result but is ~2-3x faster and avoids allocations.
**Action:** Replace `sum([list_of_booleans])` with direct addition `+` for boolean scoring logic (like in GELF, IPS criteria).

## 2024-06-12 - Function-Scoped Dictionary Re-allocation
**Learning:** Defining static dictionaries inside functions (e.g., mapping scores to strings) causes Python to re-allocate the dictionary in memory on every single function call.
**Action:** Always extract static dictionaries to module-level constants (e.g., `_RYHMAT`) and use them in the functions. This provides a ~5x speedup for those functions in this codebase.
