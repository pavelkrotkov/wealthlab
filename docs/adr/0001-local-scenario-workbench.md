# ADR 0001: Local, auditable scenario workbench

Status: accepted product direction; dependency choices pending integration spikes.

The application runs locally with a browser UI. Scenarios load explicitly from user-selected files and persist only to a selected private directory. No cloud account, telemetry, brokerage credentials or hosted database is needed.

Use a Python package and a thin Streamlit UI unless a runnable spike identifies a material limitation. Keep calculation functions independent of UI state so CLI, tests and batch comparisons use the same engine. Avoid a general plugin framework; add concrete modules for actual supported products.

Use dated economic events feeding cash, positions, liabilities and separate jurisdictional tax ledgers. Monthly household projections and annual tax reconciliation are the initial resolution. Lots, wash windows, option expiry, exercise and liquidity events require calendar dates and finer event processing; annual interpolation cannot establish margin safety. Starting midyear must accept year-to-date realized income and paid taxes without double counting.

Represent tax rules by jurisdiction and effective year. Future-law scenarios state how thresholds and rates are projected beyond verified years. Missing residency/eligibility/basis inputs produce explicit limitations or block affected outputs. No silent fallback to a flat tax rate.

Matched comparisons share initial capital, external cash flows, market paths, time horizon and valuation convention. Fees, financing, distributions, taxes and terminal unwind are explicit. Simulated harvesting must update basis and future liability. Policy decisions cannot look ahead within a path; separately identify any perfect-foresight upper bound.

Optimization first enforces spending/risk/liquidity constraints, then compares after-tax wealth. Provide a reproducible candidate table and failed constraints. Seed, dependency versions, input hash and tax-rule version accompany each export.

Quality gates for first-party Python: Radon cyclomatic complexity <= 8 for every block, Radon maintainability index >= 50 per module, <= 300 source lines per module, <= 60 physical lines per function. Apply to application, tests and tooling. Exclude only generated/third-party material explicitly. Do not game metrics by compressing statements or stripping explanatory comments. UI code receives the same checks; numerical correctness also needs independent and conservation tests.

CI follows the existing utils pattern: Ruff lint/format, ty, tests/coverage, pip-audit, actionlint, zizmor and dependency updates. Use locked dependencies, bounded workflow permissions and same-repository exact-head bot reviews. Require green checks and addressed review findings before merging implementation PRs. Initial trusted review-workflow bootstrap must be documented separately.
