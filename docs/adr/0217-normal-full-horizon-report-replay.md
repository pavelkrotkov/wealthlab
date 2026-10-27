# Normal full-horizon report replay

October 27, 2026. The existing default `horizon_example.synthetic()` household covers 624 months through age 100. Its deterministic full projection export measured 2,931,674 bytes, so the previous 2 MB decoder rejected a report produced by the ordinary supported example. Its raw inputs loaded successfully; the full monthly ledger caused the mismatch.

Raise the existing shared import bound to 200,000,000 bytes (200 MB), aligned with ordinary Streamlit upload capacity. The repository Streamlit configuration and explicit local launcher use 200 MB too. Current JSON and CSV imports continue to use the existing bound and UTF-8 handling. No new parser, compression or financial behavior is introduced. This is a bounded capacity, not a claim that arbitrarily large reports can be imported; separate input exports remain available.

One regression uses that default example and the real household engine, exports its full monthly ledger, loads it through the shared UI, ordinary/country dispatch and file readers, and checks that fresh projection reproduces the rows. Existing invalid-UTF-8 checks remain. Redundant oversized upload cases are removed rather than allocating 200 MB test inputs; the existing decoder bound check uses a small monkeypatched limit.

Validation after reconciliation with reviewed main: 30 retained report, optimizer replay, launcher, upload, CSV and UI checks passed, including the default full-horizon replay, with 91.98% combined statement/branch coverage across shared storage, native policy reports, launcher, uploads and CSV parsing. Ruff, formatting, whole-repository typing and unchanged strict metrics passed. Current-head CI and independent review remain required.
