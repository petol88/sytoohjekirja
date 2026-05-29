## 2024-04-09 - [Streamlit Rerun Loop Allocations]
**Learning:** Streamlit reruns the entire script on every user interaction. Defining static lists inside rendering loops causes redundant memory allocations and garbage collection overhead on every rerun. For small literal collections in `in` checks (e.g. `c2 in ["A", "B"]`), CPython optimizes them better if they are tuples, avoiding list creation overhead entirely.
**Action:** Always hoist static arrays (like `YKSIKKO_OPTS_BASE`) outside of loops to reuse references, and prefer tuples over lists for static options or membership checks to minimize allocation overhead per rerun.
## 2024-05-24 - Optimize ECOG Description Lookup

**Learning:** Recreating static dictionaries on every function call introduces unnecessary overhead. By hoisting these dictionaries to the module level, we can significantly reduce the execution time of simple getter functions without changing the API.
**Action:** Lifted `kuvaukset` to `_ECOG_KUVAUKSET` in `hae_ecog_kuvaus`.
## 2024-05-24 - Optimize list allocations and redundant dictionaries in calculators
**Learning:** Python's `sum([bool1, bool2, ...])` creates unnecessary list allocations and incurs function call overhead. Similarly, creating static mapping dictionaries inside function bodies re-allocates memory on every function call.
**Action:** Replace `sum([list_of_bools])` with direct addition `bool1 + bool2 + ...` (since bool inherits from int) to avoid the list overhead. Extract static dictionaries out of function bodies and define them as module-level constants (e.g., `_IPI_RISKIRYHMAT`) to ensure they are only allocated once.
