## 2024-04-09 - [Streamlit Rerun Loop Allocations]
**Learning:** Streamlit reruns the entire script on every user interaction. Defining static lists inside rendering loops causes redundant memory allocations and garbage collection overhead on every rerun. For small literal collections in `in` checks (e.g. `c2 in ["A", "B"]`), CPython optimizes them better if they are tuples, avoiding list creation overhead entirely.
**Action:** Always hoist static arrays (like `YKSIKKO_OPTS_BASE`) outside of loops to reuse references, and prefer tuples over lists for static options or membership checks to minimize allocation overhead per rerun.
## 2024-05-24 - Optimize ECOG Description Lookup

**Learning:** Recreating static dictionaries on every function call introduces unnecessary overhead. By hoisting these dictionaries to the module level, we can significantly reduce the execution time of simple getter functions without changing the API.
**Action:** Lifted `kuvaukset` to `_ECOG_KUVAUKSET` in `hae_ecog_kuvaus`.
## 2024-05-25 - Avoid sum() for Boolean Summations

**Learning:** Using `sum([bool1, bool2, ...])` incurs list allocation and function call overhead. Direct mathematical addition (`bool1 + bool2 + ...`) is significantly faster (~50% faster in micro-benchmarks).
**Action:** Replaced `sum([])` with direct addition `a + b + c` in boolean summation functions like `tarkista_gelf_kriteerit`, `laske_ips_pisteet`, and `tarkista_hl_paikallinen_riskitekijat`.

## 2024-05-25 - Hoist Inline Static Dictionaries

**Learning:** Instantiating static dictionary definitions inside a function creates unnecessary memory allocation and object creation overhead on every call.
**Action:** Lifted `ryhmat` and `ennusteet` dictionaries in `hae_ipi_riskiryhma`, `hae_cps_eg_ennuste`, and `hae_ips_ennuste` to module-level constants `_IPI_RISKIRYHMAT`, `_CPS_EG_ENNUSTEET`, and `_IPS_ENNUSTEET`.

## 2024-06-28 - Cache derived UI state mapping in Streamlit
**Learning:** Pre-calculating derived UI mappings (like protocol lists grouped by cancer type) inside a `@st.cache_data` function and returning them alongside the raw data prevents `O(N)` loop calculations on every script rerun. Using tuple lookup rather than inline calculations improves rendering time in loops dramatically.
**Action:** When filtering options dynamically based on raw data, move the pre-calculation of UI options/mappings to the caching layer to take advantage of Streamlit's rerunning behavior effectively.
