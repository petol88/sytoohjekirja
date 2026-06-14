## 2024-04-09 - [Streamlit Rerun Loop Allocations]
**Learning:** Streamlit reruns the entire script on every user interaction. Defining static lists inside rendering loops causes redundant memory allocations and garbage collection overhead on every rerun. For small literal collections in `in` checks (e.g. `c2 in ["A", "B"]`), CPython optimizes them better if they are tuples, avoiding list creation overhead entirely.
**Action:** Always hoist static arrays (like `YKSIKKO_OPTS_BASE`) outside of loops to reuse references, and prefer tuples over lists for static options or membership checks to minimize allocation overhead per rerun.
## 2024-05-24 - Optimize ECOG Description Lookup

**Learning:** Recreating static dictionaries on every function call introduces unnecessary overhead. By hoisting these dictionaries to the module level, we can significantly reduce the execution time of simple getter functions without changing the API.
**Action:** Lifted `kuvaukset` to `_ECOG_KUVAUKSET` in `hae_ecog_kuvaus`.
## 2024-05-25 - [Optimize Dictionary Instantiation and Boolean Summation]
**Learning:** Re-instantiating static dictionaries on every function call (e.g. `ryhmat = {...}`) and using `sum([bool1, bool2, ...])` inside scoring functions introduces unnecessary memory allocation and list/function call overhead. Python evaluates direct addition of booleans (e.g., `bool1 + bool2`) much faster than allocating a list and calling `sum()`.
**Action:** Extract static dictionaries to module-level constants (e.g. `_IPI_RISKIRYHMAT`) and replace `sum([...])` for boolean accumulations with direct addition to improve performance.
