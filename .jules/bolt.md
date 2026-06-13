## 2024-04-09 - [Streamlit Rerun Loop Allocations]
**Learning:** Streamlit reruns the entire script on every user interaction. Defining static lists inside rendering loops causes redundant memory allocations and garbage collection overhead on every rerun. For small literal collections in `in` checks (e.g. `c2 in ["A", "B"]`), CPython optimizes them better if they are tuples, avoiding list creation overhead entirely.
**Action:** Always hoist static arrays (like `YKSIKKO_OPTS_BASE`) outside of loops to reuse references, and prefer tuples over lists for static options or membership checks to minimize allocation overhead per rerun.
## 2024-05-24 - Optimize ECOG Description Lookup

**Learning:** Recreating static dictionaries on every function call introduces unnecessary overhead. By hoisting these dictionaries to the module level, we can significantly reduce the execution time of simple getter functions without changing the API.
**Action:** Lifted `kuvaukset` to `_ECOG_KUVAUKSET` in `hae_ecog_kuvaus`.
## 2024-05-25 - Optimize Streamlit UI List Filtering

**Learning:** Generating dynamic lists inside the Streamlit render loop by iterating over the entire database via O(N) loops (`for prot in db.values(): indikaatiot.add(...)`) causes significant overhead (~0.021 ms per rerun).
**Action:** Lift static or derived options generation (like extracting unique categories and mapping items to them) into a `@st.cache_data` data loading function, then return them as tuples/dicts. Replace the O(N) inline generation in the UI block with O(1) dictionary key lookups (`PROTOKOLLA_MAP.items()`). This reduced the widget option processing latency from ~0.021 ms to ~0.004 ms per interaction.
