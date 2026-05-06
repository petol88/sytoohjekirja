## 2024-04-09 - [Streamlit Rerun Loop Allocations]
**Learning:** Streamlit reruns the entire script on every user interaction. Defining static lists inside rendering loops causes redundant memory allocations and garbage collection overhead on every rerun. For small literal collections in `in` checks (e.g. `c2 in ["A", "B"]`), CPython optimizes them better if they are tuples, avoiding list creation overhead entirely.
**Action:** Always hoist static arrays (like `YKSIKKO_OPTS_BASE`) outside of loops to reuse references, and prefer tuples over lists for static options or membership checks to minimize allocation overhead per rerun.

## 2024-05-06 - [Streamlit Rerun Loop Caching]
**Learning:** O(N) operations in the main body of a Streamlit script cause unnecessary overhead on every widget interaction. Generating derived UI state like dictionaries or sets from raw JSON loaded via `@st.cache_data` should happen *inside* the cache function, not inside the execution flow.
**Action:** Always pre-calculate and return derived UI mappings (like protocol filter options by cancer type) as a tuple from the cached data loading function. Then, map user selections using O(1) `.get()` lookups instead of rebuilding list comprehensions in the main script body.
