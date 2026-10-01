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
## 2024-07-02 - Optimize Short Membership Checks

**Learning:** When checking if a string contains any of a small number of substrings (e.g., `any(x in t for x in ["A", "B", "C"])`), the overhead of creating a list and a generator object in Python can be significant for micro-optimizations. Expanding this to explicit `or` conditions (e.g., `"A" in t or "B" in t or "C" in t`) avoids this instantiation overhead entirely and runs purely at the C-level in CPython. This yields about a ~5x performance improvement in micro-benchmarks for this specific structure.
**Action:** Replace `any(x in str for x in ["..."])` with direct boolean `or` evaluations when the number of checks is small and static.
## 2024-05-24 - Pre-calculate dictionary keys as tuple constants for UI dropdowns
**Learning:** Calling `list(dict.keys())` dynamically in Streamlit render loops and Tkinter UI constructors incurs redundant O(N) memory allocation overhead on every script execution. Pre-computing dictionary keys as module-level tuple constants yields an ~21x performance speedup.
**Action:** Extract static UI widget options to module-level tuple constants in source modules and use tuple concatenation `("Valitse...",) + OPTS_TUPLE` when populating UI elements.
## 2024-07-28 - Pre-calculate derived UI mappings out of render loops

**Learning:** Calculating derived state from large dictionaries (e.g., extracting a unique set of all cancer types from all protocols) dynamically during a Streamlit render loop causes significant O(N) recalculation overhead on every UI interaction (~0.3ms vs ~0.002ms in micro-benchmarks).
**Action:** Extract heavy, O(N) loops that generate UI states out of the active rendering loop. Move them into the `@st.cache_data` load function and return them as pre-calculated mappings that can be unpacked with constant O(1) or minimal lookup time during the actual render.
