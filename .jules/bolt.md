## 2024-04-09 - [Streamlit Rerun Loop Allocations]
**Learning:** Streamlit reruns the entire script on every user interaction. Defining static lists inside rendering loops causes redundant memory allocations and garbage collection overhead on every rerun. For small literal collections in `in` checks (e.g. `c2 in ["A", "B"]`), CPython optimizes them better if they are tuples, avoiding list creation overhead entirely.
**Action:** Always hoist static arrays (like `YKSIKKO_OPTS_BASE`) outside of loops to reuse references, and prefer tuples over lists for static options or membership checks to minimize allocation overhead per rerun.
## 2024-05-24 - Optimize ECOG Description Lookup

**Learning:** Recreating static dictionaries on every function call introduces unnecessary overhead. By hoisting these dictionaries to the module level, we can significantly reduce the execution time of simple getter functions without changing the API.
**Action:** Lifted `kuvaukset` to `_ECOG_KUVAUKSET` in `hae_ecog_kuvaus`.
## 2024-05-24 - Optimize List and Dictionary Allocations in Python
**Learning:** Instantiating dictionaries within frequently called functions and creating inline lists purely to calculate boolean sums (e.g. `sum([a, b, c])`) introduces unnecessary overhead due to repeated memory allocations and garbage collection. Direct mathematical addition (`a + b + c`) is significantly faster for boolean variables in CPython.
**Action:** Always extract static dictionaries to module-level constants and use direct mathematical addition `+` rather than `sum([...])` for accumulating boolean conditions.
