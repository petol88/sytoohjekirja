## 2024-04-09 - [Streamlit Rerun Loop Allocations]
**Learning:** Streamlit reruns the entire script on every user interaction. Defining static lists inside rendering loops causes redundant memory allocations and garbage collection overhead on every rerun. For small literal collections in `in` checks (e.g. `c2 in ["A", "B"]`), CPython optimizes them better if they are tuples, avoiding list creation overhead entirely.
**Action:** Always hoist static arrays (like `YKSIKKO_OPTS_BASE`) outside of loops to reuse references, and prefer tuples over lists for static options or membership checks to minimize allocation overhead per rerun.
## 2024-05-24 - Optimize ECOG Description Lookup

**Learning:** Recreating static dictionaries on every function call introduces unnecessary overhead. By hoisting these dictionaries to the module level, we can significantly reduce the execution time of simple getter functions without changing the API.
**Action:** Lifted `kuvaukset` to `_ECOG_KUVAUKSET` in `hae_ecog_kuvaus`.
## 2024-05-25 - [Streamlit Derived UI State Cache]
**Learning:** Streamlit components that derive options from raw data (like extracting unique cancer types from a list of protocols) trigger O(N) calculations on every interaction if done inside the render loop. Pre-calculating these maps inside the `@st.cache_data` load function reduces widget interaction overhead from ~0.018ms to ~0.0002ms since dictionaries provide O(1) lookups.
**Action:** For class-level data loading and derived UI state in Streamlit, wrap the loading method in a `@st.cache_data` function that returns pre-calculated tuples/dictionaries, and assign them to globals or session state once per session.
