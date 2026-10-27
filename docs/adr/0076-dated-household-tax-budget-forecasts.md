# ADR 0076: Dated household tax-budget forecasts

Status: native staged-sale adapter, 2026-10-25. Extends [ADR 0029](0029-household-sale-harvest-policies.md) and reuses the standalone cumulative forecast semantics in [ADR 0004](0004-lots-and-harvesting.md). No new tax solver, tax rate or Wallet implementation is introduced.

## Forecast source and validation

`HouseholdLots.tax_budget_forecasts` holds source-labeled, dated full-year non-lot `AnnualCase` snapshots. Each confirms inclusion of known non-lot facts and assumed remaining income, exclusion of every modeled linked-lot event, and fixed forecast deductions. Source provenance must be resolved, source dates cannot follow availability, availability dates and IDs must be unique/ordered, and each policy needs a forecast already available by its decision date. Sources may predate the projection. A later-dated revision cannot inform an earlier sale.

Each active forecast supplies the native complete ordered calendar-year list. Filing units, tax policy/index assumptions, NJ regime and declared NJ retirement facts must match the actual Household context. Initial federal/NJ carry facts are preserved; later federal carries are computed separately for the with/without-lot paths, rather than entered twice. Forecast payments must be zero: these cases quote liability and cannot represent actual withholding, estimates, refunds or spending cash. Inactive forecasts are unused when no tax-budget policy is selected, allowing retained-portfolio comparisons with fixed source inputs.

The adapter does not infer eligibility, future income, paid-tax deductions or a guaranteed final tax cap. Forecast eligible NJ retirement amounts remain bounded by the existing declared Household context; future eligibility reconstruction requires another explicit adapter. The actual cash-basis NJ deduction/refund machinery remains authoritative for actual returns. Forecast deductions stay supplied assumptions and are not copied into that machinery.

## Native decision and actual execution

For a budget policy, select the latest available snapshot and create a temporary read-only `LotCase` view containing its `lot_tax_cases`. The source Household case keeps that field empty. Existing `tax_budget.choose/impact`, `tax_reporting.report` and `policy_execution.execute` use observed Book history, actual current marks, selected lots, separate bases, commissions and wash ledgers. The bounded grid/refinement finds the largest evaluated feasible sale; it makes no global-optimum claim. Full-year non-lot forecasts are assumptions, not realized future market data. Future trades, prices, income realizations and unavailable revisions cannot influence the earlier decision.

Cumulative annual tax impact includes all already-observed linked-lot disposals and separate prior carry paths. Repeated policies cannot reset the budget around the latest actual tax case and spend it again. Pending losses do not finance a benefit. Existing January observations/reconciliation remain necessary; a forecast never supplies an unknown wash outcome.

The actual Household order stays manual trades, policy sales, harvests, rebalance, one brokerage cash sweep and one recognized-gain delta with `cash_received = 0`. Forecast trials never replace the live book or become actual `TaxEvent`s, cash, payments or deductions. `TaxLedger.case` already contains earlier recognized gains and actual carry; it is not reused as an empty no-lot baseline. Current policy decisions precede later wrapper/product receipts and required funding, so those later outcomes are not used to manufacture a current forecast. Actual mandatory funding sales remain permitted even when they later exceed the estimate; essential spending is unchanged.

## Audit and UI

Sale decisions retain source ID/reference/date, availability, full snapshot fingerprint and explicitly estimated budget status. The terminal existing hidden `lot_audit.budget_audit` preserves the original estimate and requotes the same forecast after later observed trades. `tax_budget.impact(..., through_year=...)` permits an explicit already-observed past tax year for this audit; future-year quotation is rejected. Original decisions are never rewritten.

The audit separately reports actual recognized lot gains, actual return completion/provisional status, actual total liability and actual net paid cash from the real return position. Actual totals include all income/payroll; they are different quantities from a forecast incremental lot-liability delta. Information dates and cash observation dates stay separate if existing January/terminal wash assumptions finalize a prior return; the per-year audit and table explicitly mark use of a relevant post-horizon no-replacement assumption. Refund receivables remain outside spending cash until actual receipt.

Household JSON edits the forecasts directly; Markets adds an editable Tax-budget sales starter. Its entered nominal income schedules plus a labeled hypothetical unreceived annual bonus illustrate a forecast assumption, without modifying actual salary/spending schedules. Results display estimates and actual return values separately, with the non-guarantee and later-funding boundary explicit. Existing independent federal/NJ engines and public tax authorities remain those documented in ADR0004.

## Independent checks

An original one-year case has $1,000 cash and 100 shares at $100, with $5,000 federal/$6,000 NJ basis. The hypothetical full-year $200,000 bonus forecast never arrives. A $500 combined estimate permits about 49.76 shares: actual $4,976.18 sale proceeds plus opening cash leave $5,976.18 cash and $5,023.82 stock. Actual federal AGI is only the $2,488.09 realized gain, and actual federal/NJ liability/payment is zero. A repeated policy has only microshare rounding slack; it cannot spend another $500. Commissions affect actual wealth once.

Further checks preserve $9,000 mandatory essential spending even after later sales exceed the estimate; changing future market prices/manual trades/income or future-dated revisions cannot change the earlier decision. A $5,000 pending loss earns no January benefit; once mature, the forecast's $3,000 ordinary deduction at 22% and separate $2,000 carry produce a $660 first-year estimate and $300 reduction against a later external gain at 15%, with no actual unreceived refund. Partial returns, liquidity locks, source/rule/carry guards and the real editable Household form remain explicit.
