## 2024-04-09 - [Streamlit Rerun Loop Allocations]
**Learning:** Streamlit reruns the entire script on every user interaction. Defining static lists inside rendering loops causes redundant memory allocations and garbage collection overhead on every rerun. For small literal collections in `in` checks (e.g. `c2 in ["A", "B"]`), CPython optimizes them better if they are tuples, avoiding list creation overhead entirely.
**Action:** Always hoist static arrays (like `YKSIKKO_OPTS_BASE`) outside of loops to reuse references, and prefer tuples over lists for static options or membership checks to minimize allocation overhead per rerun.
## 2024-05-24 - Optimize ECOG Description Lookup

**Learning:** Recreating static dictionaries on every function call introduces unnecessary overhead. By hoisting these dictionaries to the module level, we can significantly reduce the execution time of simple getter functions without changing the API.
**Action:** Lifted `kuvaukset` to `_ECOG_KUVAUKSET` in `hae_ecog_kuvaus`.
## 2026-06-03 - Refactoring Calculators for Performance

**Learning:** In highly-called functions (like `tarkista_gelf_kriteerit` or `laske_ips_pisteet`), using `sum([bool1, bool2, ...])` creates redundant list allocations and introduces generator/function call overhead. Additionally, defining static dictionaries (like for risk groups or prognosis mappings) directly within functions (e.g. `hae_ipi_riskiryhma`) forces the dictionary to be instantiated on every call, heavily impacting iteration performance.

**Action:** Replace `sum([...])` with direct boolean-to-integer addition (e.g., `bool1 + bool2 + ...`) to avoid list allocation overhead. Extract function-level static dictionaries to module-level constants (e.g. `_IPI_RISKIRYHMAT`, `_CPS_EG_ENNUSTEET`, `_IPS_ENNUSTEET`) to prevent unnecessary allocations on each execution.
