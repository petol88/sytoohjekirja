## 2024-04-09 - [Streamlit Rerun Loop Allocations]
**Learning:** Streamlit reruns the entire script on every user interaction. Defining static lists inside rendering loops causes redundant memory allocations and garbage collection overhead on every rerun. For small literal collections in `in` checks (e.g. `c2 in ["A", "B"]`), CPython optimizes them better if they are tuples, avoiding list creation overhead entirely.
**Action:** Always hoist static arrays (like `YKSIKKO_OPTS_BASE`) outside of loops to reuse references, and prefer tuples over lists for static options or membership checks to minimize allocation overhead per rerun.
## 2024-04-09 - [Test Execution Strategy]
**Learning:** Some test suites may contain brittle tests or previously broken tests (e.g. `test_logic.py` in this workspace currently fails on `main`).
**Action:** When running test suites to verify your optimization, primarily check that your specific changes didn't introduce *new* failures. Compare test outputs before and after your change if necessary.
