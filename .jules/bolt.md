## 2024-04-09 - [Streamlit Rerun Loop Allocations]
**Learning:** Streamlit reruns the entire script on every user interaction. Defining static lists inside rendering loops causes redundant memory allocations and garbage collection overhead on every rerun. For small literal collections in `in` checks (e.g. `c2 in ["A", "B"]`), CPython optimizes them better if they are tuples, avoiding list creation overhead entirely.
**Action:** Always hoist static arrays (like `YKSIKKO_OPTS_BASE`) outside of loops to reuse references, and prefer tuples over lists for static options or membership checks to minimize allocation overhead per rerun.
## 2024-05-24 - Optimize ECOG Description Lookup

**Learning:** Recreating static dictionaries on every function call introduces unnecessary overhead. By hoisting these dictionaries to the module level, we can significantly reduce the execution time of simple getter functions without changing the API.
**Action:** Lifted `kuvaukset` to `_ECOG_KUVAUKSET` in `hae_ecog_kuvaus`.

## 2024-05-18 - [Optimize protocol filtering in Streamlit]
**Learning:** Pre-calculating derived UI mappings (like `protokolla_map` and `syopatyyppi_opts`) inside a `@st.cache_data` function avoids costly O(N) calculations and object creations during every interaction in Streamlit.
**Action:** Always aim to pre-calculate mappings inside the cache function rather than calculating on-the-fly during UI rendering, especially when dealing with dropdown lists.
