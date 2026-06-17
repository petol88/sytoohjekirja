## 2024-04-09 - [Streamlit Rerun Loop Allocations]
**Learning:** Streamlit reruns the entire script on every user interaction. Defining static lists inside rendering loops causes redundant memory allocations and garbage collection overhead on every rerun. For small literal collections in `in` checks (e.g. `c2 in ["A", "B"]`), CPython optimizes them better if they are tuples, avoiding list creation overhead entirely.
**Action:** Always hoist static arrays (like `YKSIKKO_OPTS_BASE`) outside of loops to reuse references, and prefer tuples over lists for static options or membership checks to minimize allocation overhead per rerun.
## 2024-05-24 - Optimize ECOG Description Lookup

**Learning:** Recreating static dictionaries on every function call introduces unnecessary overhead. By hoisting these dictionaries to the module level, we can significantly reduce the execution time of simple getter functions without changing the API.
**Action:** Lifted `kuvaukset` to `_ECOG_KUVAUKSET` in `hae_ecog_kuvaus`.

## 2024-05-26 - Streamlit UI Render Optimization (O(N) to O(1))
**Learning:** In Streamlit, because the entire script reruns on every user interaction, computing derived options (like filtering a dataset to populate a dropdown) inline can cause significant UI overhead as the dataset grows. In `streamlit_app.py`, calculating the `syöpatyyppi` mappings took ~0.012ms per render.
**Action:** When working with Streamlit, always move derived UI state calculations (like unique lists or filtered mappings) inside the initial `@st.cache_data` data loading function. Returning these precalculated mappings converts the inline operation to an O(1) dictionary lookup (~0.0002ms), providing a massive relative speedup with no loss of functionality.
