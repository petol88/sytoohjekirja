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
## 2024-05-25 - Avoid any() for Short Membership Checks
**Learning:** To optimize short membership checks against a known set of items, use explicit `or` conditions (e.g., `"A" in t or "B" in t`) instead of generator expressions like `any(x in t for x in ["A", "B"])`. Explicit `or` evaluates at the C-level in CPython, avoiding generator instantiation overhead and yielding a ~5-10x performance improvement.
**Action:** Replaced `any(x in t for x in ["T2c", "T3", "T4"])` with `"T2c" in t or "T3" in t or "T4" in t` in `laske_riskiryhma_eturauhassyopa`.
