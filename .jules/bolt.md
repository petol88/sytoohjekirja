## 2024-04-09 - [Streamlit Rerun Loop Allocations]
**Learning:** Streamlit reruns the entire script on every user interaction. Defining static lists inside rendering loops causes redundant memory allocations and garbage collection overhead on every rerun. For small literal collections in `in` checks (e.g. `c2 in ["A", "B"]`), CPython optimizes them better if they are tuples, avoiding list creation overhead entirely.
**Action:** Always hoist static arrays (like `YKSIKKO_OPTS_BASE`) outside of loops to reuse references, and prefer tuples over lists for static options or membership checks to minimize allocation overhead per rerun.

## 2024-05-09 - [Streamlit Caching for Derived Data]
**Learning:** In Streamlit applications, deriving dropdown options and mappings (like cancer types and their associated protocols) from a large backend data dictionary during the main render loop causes an O(N) performance hit on *every single UI interaction*.
**Action:** Move derived data calculations into the initial data-loading function wrapped with `@st.cache_data`. This ensures that expensive string matching, list sorting, and set operations are performed only once upon loading the data, reducing widget interaction overhead from O(N) to O(1) dictionary lookups.
