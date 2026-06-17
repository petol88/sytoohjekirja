## 2024-04-09 - [Streamlit Rerun Loop Allocations]
**Learning:** Streamlit reruns the entire script on every user interaction. Defining static lists inside rendering loops causes redundant memory allocations and garbage collection overhead on every rerun. For small literal collections in `in` checks (e.g. `c2 in ["A", "B"]`), CPython optimizes them better if they are tuples, avoiding list creation overhead entirely.
**Action:** Always hoist static arrays (like `YKSIKKO_OPTS_BASE`) outside of loops to reuse references, and prefer tuples over lists for static options or membership checks to minimize allocation overhead per rerun.
## 2024-05-24 - Optimize ECOG Description Lookup

**Learning:** Recreating static dictionaries on every function call introduces unnecessary overhead. By hoisting these dictionaries to the module level, we can significantly reduce the execution time of simple getter functions without changing the API.
**Action:** Lifted `kuvaukset` to `_ECOG_KUVAUKSET` in `hae_ecog_kuvaus`.

## 2025-06-17 - [Extract Inline Dicts to Module-level Constants]
 **Learning:** In Python, creating a dictionary inside a function using a literal (e.g. `ryhmat = {0: "...", ...}`) incurs memory allocation and object creation overhead *every time the function is called*. For static configurations or lookup tables, hoisting these definitions out of the function body and storing them as module-level constants dramatically improves function execution time (from ~0.44s to ~0.08s for 1M iterations in basic benchmarks).
 **Action:** Proactively check for static dictionary or list instantiations inside frequently called functions, particularly helper functions or calculation handlers, and extract them to module-level constants.
