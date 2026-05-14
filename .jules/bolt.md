## 2024-04-09 - [Streamlit Rerun Loop Allocations]
**Learning:** Streamlit reruns the entire script on every user interaction. Defining static lists inside rendering loops causes redundant memory allocations and garbage collection overhead on every rerun. For small literal collections in `in` checks (e.g. `c2 in ["A", "B"]`), CPython optimizes them better if they are tuples, avoiding list creation overhead entirely.
**Action:** Always hoist static arrays (like `YKSIKKO_OPTS_BASE`) outside of loops to reuse references, and prefer tuples over lists for static options or membership checks to minimize allocation overhead per rerun.

## 2024-04-10 - [Streamlit Rerun Loop Dropdowns]
**Learning:** In Streamlit, calculating dropdown options dynamically inside the rendering loop via iterating over large data dictionaries is highly inefficient because it executes O(N) operations on *every* user interaction or text input.
**Action:** Always pre-calculate derived UI mappings inside the `@st.cache_data` load function. Expose O(1) dictionary lookups (`protokolla_map.get(syopatyyppi)`) to the render flow, reducing UI interaction overhead significantly.
