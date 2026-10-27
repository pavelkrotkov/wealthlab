# Model coverage and release limits

October 25, 2026. Baseline: main `6cd0cf43a7fa74215fc62b6f8fcfeba99a784868` plus this local launch/report/path layer. [Issue #19](https://github.com/pavelkrotkov/wealthlab/issues/19) remains open. A pending PR or green isolated test is not a merged integrated release. Each named UI workbench has editable synthetic inputs and its own explicit assumptions; the table summarizes major boundaries rather than replacing its owning ADR.

| Area | Current UI / verification path | Material boundary |
|---|---|---|
| Household | Household editor, baseline clone, selected private save/import and shared CLI reports | Enabled plans only; the default synthetic example omits taxes. Monthly sequencing does not prove intramonth liquidity. |
| Federal/NJ | Annual tax; Household tax assumptions and annual settlement/audit | Published versus frozen future rules, independent state basis/categories and supplied recognition. [Tax coverage](tax-rules.md) remains authoritative for unsupported forms. |
| Lots and concentration | Tax lots; actual-lot Household loaders; Markets staged/concentration/harvest/rebalance cases | Actual dated lots, permitted sales, wash relationships and lock coverage are required; no invented quote or absent basis. |
| Retirement | Retirement workbenches and named Household loaders | [Retirement coverage](retirement-coverage.md) lists supported claims, wrappers and exceptions. The recommended full install includes Owl production FRA/RMD data; core-only installs block applicable cases. Whole-record tax, benefit or RMD completeness is not inferred from a balance. |
| Employment | Household employment/employer-compensation/linked-shock loaders | Supplied vesting, source withholding, employment/asset correlation and contractual rights; no inferred plan terms. |
| Markets | Markets factors and Household funding with matched realized paths | Finite supplied horizons, sample uncertainty, explicit historical coverage and no assumed future quotes. Factor growth alone is not spending safety. |
| Long/short and private fund | Products economics/conditional fund; Household and Markets profiles | Explicit dealing, margin/recourse, liquidity and independently supplied tax facts. Legal eligibility and automatic K-1 reconstruction are not inferred. |
| Traditional exchange fund | Products / Traditional exchange funds | Conditional acceptance/lockup/fees and independent bases; eventual taxable basket sale. Tax deferral is not elimination. |
| Options | Products overlays; actual-option Household and bounded Markets paths | Leg marks, assignment, collateral and supplied tax classification; no historical option-surface inference. |
| Whole life / saving | Products illustration, actual contract and matched saving comparisons; Household loaders | Supplied schedule/contract/MEC assumptions, actual loans/taxes and separate protection cost. DIR is not policy IRR; marked wealth differs from completed exit wealth. |
| CLI and local reports | `python -m wealthlab project`, `compare`, `serve`; projection export/import | Uses the same monthly household engine. Does not offer unsupported standalone product optimization or a bilateral tax certificate. |
| Opportunity-zone funds | [Issue #12](https://github.com/pavelkrotkov/wealthlab/issues/12), pending PR114/118 | Not part of this main-based release baseline; current-head review and integration remain required. |
| Drilling | [Issue #13](https://github.com/pavelkrotkov/wealthlab/issues/13), pending PR110/112 | Conditional full-tax scope and supplied K-1/SE/QBI/AMT facts; not a merged release feature here. |
| Puerto Rico | [Issue #15](https://github.com/pavelkrotkov/wealthlab/issues/15), pending owning stack | Residency/source/incentive eligibility is not inferred; pending jurisdiction work is not a supported universal exemption. |
| Spain | [Issue #16](https://github.com/pavelkrotkov/wealthlab/issues/16), pending PR129/131/135 | Common-regime annual assessments, independently classified products and pure obligation bridge; pending merge/review. No second cash book or automatic bilateral credits. |
| Cross-border | [Issue #17](https://github.com/pavelkrotkov/wealthlab/issues/17), active independent implementation | One dated payment/refund/funding/credit book is still required; do not add US/Spain total taxes or take their maximum. |
| Bounded optimizer | [Issue #18](https://github.com/pavelkrotkov/wealthlab/issues/18), active owning stack | Search/validation separation, supported accounts/products and completed exits must be integrated and reviewed. Current CLI comparison is not that optimizer. |
| Complete release | [Issue #19](https://github.com/pavelkrotkov/wealthlab/issues/19) | All merged slices, current-head CI/reviews, full workflow and browser checks must be re-observed together. This layer does not close the dependency chain. |

Before relying on a result, resolve its blocked assumptions and inspect its actual enabled plans, funding failures, outstanding claims/debt, completed-exit convention and source provenance. A tax deduction, assessed credit, unexecuted exit or hypothetical preferred return never becomes spendable cash by itself.
