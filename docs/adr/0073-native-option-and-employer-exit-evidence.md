# ADR 0073: Native option and employer exit evidence

Status: native observer layer for optimizer integration, 2026-10-25. Continues [ADR 0071](0071-household-options.md) and [ADR 0014](0014-employer-compensation.md). The optimizer adapter is owned separately.

## Decision

Export actual native state rather than treating zero marked account equity as a complete exit. Observation never prices, trades, repays debt, funds collateral, moves household cash or changes tax recognition. In particular it does not call the option snapshot helper, whose margin calculation can fund collateral.

`wealthlab.products.option_exit_state.evidence(state, observed_at)` supplies:

- Full active contract terms/IDs and actual remaining stock lots/owned shares, including separately dated future openings.
- Post-execution inside/outside cash, negative settlement cash payable, actual settlement loan, reserved collateral, native book fees and earned dividend receivables/entitlements.
- Native borrowed shares of zero with its explicit validated long-only/no-stock-borrow scope. This model cannot oversell lots or invent stock borrowing to satisfy physical delivery. External borrowing remains unknown; cash borrowing is a separate actual liability.
- Separate recorded-position closure, conservative modeled cash-exit completion and execution history. Completion requires no remaining contracts/lots/future openings, debt/collateral/fees/negative cash/dividend receivables, or execution failures. A native `complete_unwind` phase alone does not establish these conditions.

Standalone option results include `exit_state`. Household results put the post-settle observation on the terminal record of the existing hidden `option_mark_audit`, after free cash has actually reached Wallet and loan repayments have occurred. `option_exit_state.from_rows(rows)` provides the public consumer seam; missing evidence is unknown. No new nested household table column or shared UI change is needed. Tax settlement is explicitly separate and unproved by this book observer; the optimizer must retain the generic actual tax/cash checks.

`wealthlab.employment.compensation_exit_state.evidence(ledger, wallet, tranche, end)` exports the actual vested/unvested dollar state, account reconciliation, funded distribution cash, forfeited value, market losses, full-zero market events, disposition source/bucket/election and declared future events within the supplied horizon. The original compensation event log now retains distribution bucket, purpose and election. Full forensic lists are attached only to terminal `employer_tranches` records, avoiding quadratic projection output across simulation paths. Direct native-ledger observation remains available at an intermediate cutoff. `compensation_exit_state.from_rows(rows)` extracts the final tranche evidence.

An employer tranche has dollar values, not contractual units or a legal termination state. A return of -100%, or cent rounding to zero, therefore does not prove that the contract disappeared. Separate deferred rights, remaining units, contractual closure and post-horizon rights/obligations remain explicitly unknown in this layer even if actual cash distribution and forfeiture have exhausted the recorded dollar values. Supplied tax allocations compile separately into TaxPlan, so runtime absence of an allocation event does not prove no future tax obligation; consumers must inspect original inputs and the actual tax position.

A dependent adapter may accept explicit sourced/supplied termination, remaining-rights and obligation facts. It must reconcile actual books/cash/taxes and dated events; it may not infer a legal termination from a market writeoff or silently drop future grants or allocations. Until then the optimizer must preserve the affected contractual-exit guard.

## Native cash and uncertainty oracles

- A complete one-leg stock/option unwind leaves $28,500 inside/outside cash, no contracts/lots or collateral, without double-counting the premium.
- Equal opposite modeled option marks can net to zero while two actual contracts remain; they are not an exit.
- A short cash call receiving $500 and owing $90,000 retains $89,500 unpaid settlement debt without invented limited liability. With explicitly zero-interest permitted financing, the same amount remains a cash loan. Either can survive a `complete_unwind` label.
- Failed physical delivery retains the active contract and creates no borrowed shares. A rejected stock sale preserves the actual 100-share lot. Ex-date dividend rights survive actual sale/close until the later $100 payment.
- The native household assignment still ends with $6,500 cash/net wealth; the option book's terminal cash is zero after the actual Wallet sweep, not the earlier gross snapshot.
- An employer $110,000 total writeoff produces no cash redemption and preserves its separately supplied $20,000 tax allocation. The synthetic household still ends at $174,980, with no inferred loss deduction or termination.
- A funded $20,000 vested distribution plus explicit $80,000 unvested forfeiture changes cash by $20,000 relative to retaining the distribution while preserving matched taxes/wealth. Actual dollar disposition is auditable; legal units/closure remain unknown without separate facts.

These are original synthetic records and native accounting checks, not adviser terms, market quote history or legal determinations.
