## 2024-04-09 - [Streamlit Rerun Loop Allocations]
**Learning:** Streamlit reruns the entire script on every user interaction. Defining static lists inside rendering loops causes redundant memory allocations and garbage collection overhead on every rerun. For small literal collections in `in` checks (e.g. `c2 in ["A", "B"]`), CPython optimizes them better if they are tuples, avoiding list creation overhead entirely.
**Action:** Always hoist static arrays (like `YKSIKKO_OPTS_BASE`) outside of loops to reuse references, and prefer tuples over lists for static options or membership checks to minimize allocation overhead per rerun.
## 2024-05-24 - Optimize ECOG Description Lookup

**Learning:** Recreating static dictionaries on every function call introduces unnecessary overhead. By hoisting these dictionaries to the module level, we can significantly reduce the execution time of simple getter functions without changing the API.
**Action:** Lifted `kuvaukset` to `_ECOG_KUVAUKSET` in `hae_ecog_kuvaus`.
## 2024-06-02 - Optimize Calculators Boolean Operations and Lookup Performance

**Learning:** Re-instantiating constant dictionaries (such as mapping dictionaries for risk grouping or prognosis) inside of function bodies creates severe overhead in frequently called pure functions. Moving these definitions to the module scope avoids recreating them on every call. In addition, python's built in `sum([bool1, bool2, ...])` allocates a new list every call and invokes the function overhead of `sum()`. Using direct boolean addition `bool1 + bool2 + bool3` relies on python's fast evaluation of bools as ints resulting in more than a 2x performance increase.
**Action:** Extract constant dictionaries to module-level variables (e.g. `_IPI_RISKIRYHMAT`, `_CPS_EG_ENNUSTEET`, `_IPS_ENNUSTEET`) and replaced list allocations inside `sum()` in calculator metrics algorithms (`tarkista_gelf_kriteerit`, `laske_ips_pisteet`, `tarkista_hl_paikallinen_riskitekijat`) with native addition operations.
