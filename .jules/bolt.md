## 2024-04-09 - [Streamlit Rerun Loop Allocations]
**Learning:** Streamlit reruns the entire script on every user interaction. Defining static lists inside rendering loops causes redundant memory allocations and garbage collection overhead on every rerun. For small literal collections in `in` checks (e.g. `c2 in ["A", "B"]`), CPython optimizes them better if they are tuples, avoiding list creation overhead entirely.
**Action:** Always hoist static arrays (like `YKSIKKO_OPTS_BASE`) outside of loops to reuse references, and prefer tuples over lists for static options or membership checks to minimize allocation overhead per rerun.
## 2024-05-24 - Optimize ECOG Description Lookup

**Learning:** Recreating static dictionaries on every function call introduces unnecessary overhead. By hoisting these dictionaries to the module level, we can significantly reduce the execution time of simple getter functions without changing the API.
**Action:** Lifted `kuvaukset` to `_ECOG_KUVAUKSET` in `hae_ecog_kuvaus`.
## 2024-05-25 - Precompute Derived UI State in @st.cache_data

**Learning:** Extracting lists or looping over data to filter UI options during a Streamlit page render blocks the UI thread and runs in O(N) time on every state change. For application metadata like protocol lists by indication, calculating the full `key -> [values]` map inside the `@st.cache_data` loader function and returning it as a cached tuple reduces the operation to an O(1) dictionary lookup during the render cycle.
**Action:** When filtering a dataset to populate UI selectboxes in Streamlit, pre-calculate the filtering map inside the data loader and use `st.selectbox(..., map.get(selection, []))` to prevent O(N) loops on every widget interaction.
