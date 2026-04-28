## 2024-04-09 - [Streamlit Rerun Loop Allocations]
**Learning:** Streamlit reruns the entire script on every user interaction. Defining static lists inside rendering loops causes redundant memory allocations and garbage collection overhead on every rerun. For small literal collections in `in` checks (e.g. `c2 in ["A", "B"]`), CPython optimizes them better if they are tuples, avoiding list creation overhead entirely.
**Action:** Always hoist static arrays (like `YKSIKKO_OPTS_BASE`) outside of loops to reuse references, and prefer tuples over lists for static options or membership checks to minimize allocation overhead per rerun.
## 2024-04-28 - [Streamlit Pre-calculate UI state and mappings]
**Learning:** In Streamlit, inline O(N) operations and set-based uniqueness aggregations within the render pipeline add significant computational overhead on each rerun.
**Action:** When extracting dropdown items and building mappings from the primary data structure (`Tietokanta.data`), perform the extraction inside the `@st.cache_data` decorated data loader and return the derived collections. Use these cached structures directly in the UI components.
