## 2024-04-09 - [Streamlit Rerun Loop Allocations]
**Learning:** Streamlit reruns the entire script on every user interaction. Defining static lists inside rendering loops causes redundant memory allocations and garbage collection overhead on every rerun. For small literal collections in `in` checks (e.g. `c2 in ["A", "B"]`), CPython optimizes them better if they are tuples, avoiding list creation overhead entirely.
**Action:** Always hoist static arrays (like `YKSIKKO_OPTS_BASE`) outside of loops to reuse references, and prefer tuples over lists for static options or membership checks to minimize allocation overhead per rerun.
## 2024-05-24 - Optimize ECOG Description Lookup

**Learning:** Recreating static dictionaries on every function call introduces unnecessary overhead. By hoisting these dictionaries to the module level, we can significantly reduce the execution time of simple getter functions without changing the API.
**Action:** Lifted `kuvaukset` to `_ECOG_KUVAUKSET` in `hae_ecog_kuvaus`.
## 2024-05-24 - Pre-calculate Derived UI Mappings

**Learning:** Computing derived UI mappings (like filtering a protocol list based on a selected cancer type) inside the main Streamlit render path causes O(N) recalculations on every interaction. This can add significant overhead (e.g. ~0.02ms vs ~0.0001ms) as the dataset grows.
**Action:** Move the pre-calculation of derived UI state into the `@st.cache_data` load function and return a pre-computed mapping (e.g., `protokolla_map`), allowing the render path to perform an O(1) dictionary lookup instead of filtering lists.
