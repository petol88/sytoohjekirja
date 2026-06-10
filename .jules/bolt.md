## 2024-04-09 - [Streamlit Rerun Loop Allocations]
**Learning:** Streamlit reruns the entire script on every user interaction. Defining static lists inside rendering loops causes redundant memory allocations and garbage collection overhead on every rerun. For small literal collections in `in` checks (e.g. `c2 in ["A", "B"]`), CPython optimizes them better if they are tuples, avoiding list creation overhead entirely.
**Action:** Always hoist static arrays (like `YKSIKKO_OPTS_BASE`) outside of loops to reuse references, and prefer tuples over lists for static options or membership checks to minimize allocation overhead per rerun.
## 2024-05-24 - Optimize ECOG Description Lookup

**Learning:** Recreating static dictionaries on every function call introduces unnecessary overhead. By hoisting these dictionaries to the module level, we can significantly reduce the execution time of simple getter functions without changing the API.
**Action:** Lifted `kuvaukset` to `_ECOG_KUVAUKSET` in `hae_ecog_kuvaus`.
## 2024-05-24 - [Avoid `sum` for Booleans]
**Learning:** Using the built-in `sum()` function with a list of booleans (e.g., `sum([bool1, bool2])`) is significantly slower (around ~170ns) than direct mathematical addition (`bool1 + bool2`, around ~20ns). This is because Python allocates a new list in memory and then invokes the `sum()` function, whereas direct addition takes advantage of the fact that `bool` is a subclass of `int` in Python.
**Action:** Replace `sum([bool1, bool2, ...])` with `bool1 + bool2 + ...` to avoid unnecessary list allocation and function call overhead, particularly in frequently called functions.
