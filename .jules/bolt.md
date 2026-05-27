## 2024-04-09 - [Streamlit Rerun Loop Allocations]
**Learning:** Streamlit reruns the entire script on every user interaction. Defining static lists inside rendering loops causes redundant memory allocations and garbage collection overhead on every rerun. For small literal collections in `in` checks (e.g. `c2 in ["A", "B"]`), CPython optimizes them better if they are tuples, avoiding list creation overhead entirely.
**Action:** Always hoist static arrays (like `YKSIKKO_OPTS_BASE`) outside of loops to reuse references, and prefer tuples over lists for static options or membership checks to minimize allocation overhead per rerun.
## 2024-05-24 - Optimize ECOG Description Lookup

**Learning:** Recreating static dictionaries on every function call introduces unnecessary overhead. By hoisting these dictionaries to the module level, we can significantly reduce the execution time of simple getter functions without changing the API.
**Action:** Lifted `kuvaukset` to `_ECOG_KUVAUKSET` in `hae_ecog_kuvaus`.

## 2024-05-18 - [Python Memory & Function Calling Overhead]
**Learning:** Python's `sum([a, b, c])` creates a temporary list in memory and introduces function call overhead. For summing explicit boolean values, `a + b + c` is significantly faster. Similarly, local dictionaries declared inside functions are re-instantiated and allocated in memory on every call, heavily impacting performance for frequently called risk/staging parsers.
**Action:** Extract static dictionaries to module-level constants. Replace `sum([...])` with direct addition `+` when the elements are explicit boolean arguments.
