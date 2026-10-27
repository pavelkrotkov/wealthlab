# Model coverage and release limits

October 27, 2026. This country-report layer is based on reviewed main `cc28c676e66ad247f2970108ff21bc244b52666d`. [Issue #19](https://github.com/pavelkrotkov/wealthlab/issues/19) remains open until integrated checks and current-head independent review pass. Each workbench retains its explicit assumptions; this table does not replace its owning ADR.

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
| CLI and local reports | `python -m wealthlab project`, `compare`, `serve`; ordinary and country projection export/import | Reexecutes complete original inputs through the same household or native country engine. Does not establish a bilateral tax certificate. |
| Opportunity-zone funds | [Issue #12](https://github.com/pavelkrotkov/wealthlab/issues/12), pending PR114/118 | Not part of this main-based release baseline; current-head review and integration remain required. |
| Drilling | [Issue #13](https://github.com/pavelkrotkov/wealthlab/issues/13), pending PR110/112 | Conditional full-tax scope and supplied K-1/SE/QBI/AMT facts; not a merged release feature here. |
| Puerto Rico | Cross-border / Country cash; native PR source/gain/credit profiles | Residency, source and incentive eligibility remain explicit conditional inputs; no universal exemption is inferred. |
| Spain | Cross-border / Country cash; complete Spain inputs and report replay | Common-regime assessments retain the independent Spain context. Foreign relief stays explicit; no automatic bilateral credits or second cash book. |
| Cross-border | Country cash, shared payment/refund/funding/credit records and aligned UI/CLI comparisons | Complete PR/Spain inputs reexecute both country assessments and actual shared cash. Archived outcomes are ignored; relocation is not an automatic search control. |
| Bounded optimizer | [Issue #18](https://github.com/pavelkrotkov/wealthlab/issues/18), active owning stack | Search/validation separation, supported accounts/products and completed exits must be integrated and reviewed. Current CLI comparison is not that optimizer. |
| Complete release | [Issue #19](https://github.com/pavelkrotkov/wealthlab/issues/19) | All merged slices, current-head CI/reviews, full workflow and browser checks must be re-observed together. This layer does not close the dependency chain. |

Before relying on a result, resolve its blocked assumptions and inspect its actual enabled plans, funding failures, outstanding claims/debt, completed-exit convention and source provenance. A tax deduction, assessed credit, unexecuted exit or hypothetical preferred return never becomes spendable cash by itself.
