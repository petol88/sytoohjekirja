## 2024-04-09 - [Streamlit Rerun Loop Allocations]
**Learning:** Streamlit reruns the entire script on every user interaction. Defining static lists inside rendering loops causes redundant memory allocations and garbage collection overhead on every rerun. For small literal collections in `in` checks (e.g. `c2 in ["A", "B"]`), CPython optimizes them better if they are tuples, avoiding list creation overhead entirely.
**Action:** Always hoist static arrays (like `YKSIKKO_OPTS_BASE`) outside of loops to reuse references, and prefer tuples over lists for static options or membership checks to minimize allocation overhead per rerun.
## 2024-05-24 - Optimize ECOG Description Lookup

**Learning:** Recreating static dictionaries on every function call introduces unnecessary overhead. By hoisting these dictionaries to the module level, we can significantly reduce the execution time of simple getter functions without changing the API.
**Action:** Lifted `kuvaukset` to `_ECOG_KUVAUKSET` in `hae_ecog_kuvaus`.
## 2026-06-18 - [Optimize Boolean Summation in Python]
**Learning:** In Python, `sum([bool1, bool2, ...])` requires allocating a list in memory and involves a function call overhead. Directly adding boolean values like `bool1 + bool2 + ...` is evaluated immediately without extra allocations, yielding an approximately 2.5x speedup for small sets of inputs based on `timeit` testing.
**Action:** Avoid using `sum([...])` for simple boolean sum operations. Use direct addition (`+`) instead to minimize memory overhead and execution time.
