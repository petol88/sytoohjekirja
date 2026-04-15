## 2024-04-09 - [Streamlit Rerun Loop Allocations]
**Learning:** Streamlit reruns the entire script on every user interaction. Defining static lists inside rendering loops causes redundant memory allocations and garbage collection overhead on every rerun. For small literal collections in `in` checks (e.g. `c2 in ["A", "B"]`), CPython optimizes them better if they are tuples, avoiding list creation overhead entirely.
**Action:** Always hoist static arrays (like `YKSIKKO_OPTS_BASE`) outside of loops to reuse references, and prefer tuples over lists for static options or membership checks to minimize allocation overhead per rerun.

## 2024-04-14 - [Streamlit Costly Loop O(N) Reductions]
**Learning:** When generating dropdown menus from a large backend data dictionary in a Streamlit app, iterating through all values (O(N) operations) during the render cycle introduces unnecessary latency.
**Action:** Use Streamlit's `@st.cache_data` (e.g. `load_data()`) to pre-calculate metadata mappings (like aggregating unique dropdown categories or mapping categories to choices) during the initial data load, reducing the render cycle to simple O(1) dictionary lookups.
