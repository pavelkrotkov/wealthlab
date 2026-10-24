# ADR 0034: Actual household long/short cash and recourse debt

Status: household integration layer of open ticket #9, building on [the economic book](0033-long-short-economics.md). Conditional tax-treatment controls, basis/exit reconstruction and the separate private-fund contract remain required. No new dependency.

## One cash source and one liability

An optional sleeve plan owns known USD taxable accounts with reconciled opening equity. It cannot share an actual-lot account, generic contribution destination or permitted taxable funding source. Generic account fees are excluded from this profile; economic manager/transaction costs remain in its supplied terms. The standalone outside-cash input must be zero: actual household cash supplies collateral.

The product hook runs after current receipts and prior tax arrears, before optional HSA/529/IRA deposits and current taxes/spending. Existing employee payroll elections retain their payroll priority. Accounts execute in supplied order. Only the net movement between each economic book and the wallet is applied; redemptions do not create another tax-event cash receipt. A closed account's remaining recourse debt uses later available household receipts, with unpaid debt retaining the supplied financing cost.

Positive net equity updates the account balance. Negative equity becomes a separate liability deducted once from household wealth. The loan already inside positive equity is not deducted again. Unresolved margin, negative equity and blocked requested terminal exits are product constraints, separately counted from consumption shortfalls. Configured liquidation can resolve a collateral shortfall. Optional unfilled redemption requests are not extra spending bills. Actual inability to meet spending/taxes still appears through the ordinary cash ledger.

## Observations, recognition and coverage

Dated observations must cover every complete projection month in order, with resolved provenance and unique observation/allocation/policy IDs. Manual month-end observations or explicit same-batch market bindings use the same economic step. A binding requires confirmation to replace entered observations, maps the case's long/short factors and retains the original source. Generated rates use twelve decimal places; ordinary cent-rounded accounting remains authoritative. Locks preserve both legs and debt.

Tax recognition is supplied separately using supported federal capital/passive/interest/dividend fields and NJ disposition/business/interest/dividend/other fields. Wage, pension, personal deduction and manual carry inputs cannot be introduced through this allocation adapter. Actual zero-cash allocations enter the same completed annual return, tax-payment funding and carry calculations. The caller confirms complete supplied recognition/exit assumptions and exclusion from other tax facts. Fixed illustrations do not vary automatically with simulated prices and do not establish a deduction, basis or legal classification. No tax-saving cash is deposited.

The Markets outcome separately counts margin triggers, unresolved margin, negative-equity months and blocked requested exits, with product and joint feasibility alongside cash-funding success. Factor exposures retain positive long and negative short notionals, while issuer inventory remains unknown. First-period opening holdings and positive contingent/gross positions preserve missing issuer coverage even after an account's net equity reaches zero or its positions exit. This prevents apparent concentration safety from an incomplete observation.

## UI and checks

The Household page loads/edits a synthetic sleeve plan and shows cash, positions and recourse debt. Markets / Household funding offers **Long-short household**, including a short-squeeze stress, and paired policies keep the same realized batch. Audits/export retain both original terms and actual economic steps. The synthetic horizon is not a lifetime retirement-safety demonstration.

Checks reconcile a $120,000 squeeze loss against $110,000 opening household capital to a $10,000 liability, without a duplicate consumption shortfall. A later $3,000 receipt reduces that liability to $7,000 exactly once. A $20,000 redemption funds $20,000 spending once; a lock leaves that spending unpaid while preserving assets. Supplied noncash gains change the actual annual tax return without creating cash. Paired unlevered/squeeze cases differ by $120,000; negative net equity retains gross factor exposure and unknown issuer coverage. Scope/mapping guards, immutable source inputs, both actual UI forms and existing household/retirement/market regressions are included.


## Funding and constraint outcomes

Cash-funding success records actual unpaid household bills and taxes. A pre-unwind collateral deficit is diagnostic: a configured liquidation that clears obligations is a valid response. Unresolved margin means the required unwind is blocked. Negative-equity months and blocked requested terminal exits are separate constraints. Product feasibility requires no such unresolved constraint over the path; joint feasibility requires both product feasibility and cash funding. These categories are reported independently rather than calling every debt month another missed margin call.

The supplied cash-priority convention uses available wallet cash at the sleeve hook. Dated lot-policy sales before that hook can pre-fund calls; automatic general spending/tax funding sales occur later. This layer does not infer a pledge or automatic sale of other accounts for collateral.
