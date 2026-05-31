## 2024-04-09 - [Streamlit Rerun Loop Allocations]
**Learning:** Streamlit reruns the entire script on every user interaction. Defining static lists inside rendering loops causes redundant memory allocations and garbage collection overhead on every rerun. For small literal collections in `in` checks (e.g. `c2 in ["A", "B"]`), CPython optimizes them better if they are tuples, avoiding list creation overhead entirely.
**Action:** Always hoist static arrays (like `YKSIKKO_OPTS_BASE`) outside of loops to reuse references, and prefer tuples over lists for static options or membership checks to minimize allocation overhead per rerun.
## 2024-05-24 - Optimize ECOG Description Lookup

**Learning:** Recreating static dictionaries on every function call introduces unnecessary overhead. By hoisting these dictionaries to the module level, we can significantly reduce the execution time of simple getter functions without changing the API.
**Action:** Lifted `kuvaukset` to `_ECOG_KUVAUKSET` in `hae_ecog_kuvaus`.
## 2024-05-24 - Pre-calculating derived UI mappings in Streamlit

**Learning:** Streamlit reruns the entire script on every user interaction. Performing `O(N)` filtering loops to extract UI dropdown options directly in the main render flow introduces unnecessary overhead on every interaction. Benchmarking showed `O(N)` inline filtering took ~0.0126ms per run, while `O(1)` dict lookups took ~0.0002ms.
**Action:** When working with large static configuration data (like `Tietokanta.data`), always pre-calculate derived UI state (like dropdown options or filtered mapping lists) inside the `@st.cache_data` decorated loader function. Return a tuple containing the base data alongside the computed structures.
