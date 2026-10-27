# ADR 0081: Native exchange allocation and retained-source exits

Status: implemented native product control above the existing exchange fund in ADR0080. Independent of the optimizer and release stacks. No new dependency, sponsor term or legal eligibility rule.

## Actual capital and zero contribution

`contribution_quantity` may be zero, partial or the entire actual source lot. Its original opening shares/price still reconcile to the same source-account balance. Positive contributions use the existing lot split with independent federal/NJ bases; zero skips contribution/disposal, basket creation and fund allocation events entirely. There is no synthetic cash transfer or second source account. Zero-contribution cases reject nonzero supplied monthly fund cash, tax income/loss or basis adjustments, rather than silently scaling independently supplied facts to produce a favorable result. Positive allocation choices retain the same fixed contract/tax facts; an infeasible distribution/basis schedule remains blocked.

Zero does not establish sponsor acceptance or legal qualification. It opens no fund even if the supplied conditional contract would accept a positive contribution. A denied acceptance likewise retains all actual source shares and charges no fund NAV fees. The audit distinguishes fund entry, active interest, actual remaining shares and conditional modeled exit status.

An opening source lot must already exist. A positive opening contribution still requires it to be liquid at opening. A retained-only lot may have a later supplied liquidity date; its actual value stays restricted and cannot fund spending through a blocked source sale. Source-account overlap and the existing known no-external-identical-trade/wash scope remain unchanged.

## Native dated source sale

A month-end `sell_source` request sells all actual retained source positions in one ordinary `Book.trade`, using specific lot IDs, their actual acquisition/holding dates, independent bases and that month's supplied source mark. Source identity follows the security rather than the original lot ID: wash allocation may split retained stock into new lot IDs. `sell_liquid` continues to sell only the distributed/directly purchased basket and cannot accidentally consume such source pieces.

A source lot or observation/account lock denies the source order without mutating shares, basis or cash. The denial does not automatically retry when a lock expires; a later explicit order is needed. A request with no remaining source is an audited no-op. Source orders neither redeem the fund nor certify that a retained active interest is closed.

The shared existing wash/NJ recognition path produces an actual zero-cash tax event from executed disposal rows. Actual broker-book proceeds enter the household wallet exactly once through the existing monthly cash drain. They are not deposited a second time as taxable-event cash or a headline tax saving. The monthly execution retains the existing same-date cash convention; it does not infer actual broker settlement dates or intramonth liquidity.

## Values and complete-exit boundaries

Account value is actual marked source/basket shares plus actual fund NAV. Restricted value is a separate subset: active fund NAV plus actual lot/market-locked shares. Adding a restriction must not create another asset balance. Unlocked shares remain distinct from wallet cash; there is no automatic product sale for a bill.

Monthly source quantities/bases, basket-lot count and position closure derive from the actual ending book and active-interest state. Zero NAV alone never closes held stock, an active interest or an unsold basket. Final `exit_status` separately retains pending recognition events and wash positions; `modeled_exit_complete` requires actual positions closed and no such modeled pending items. It remains conditional, and `full_tax_optimization_supported` stays false. Household unpaid taxes/receivables, source legal assumptions and any broader terminal certificate still belong to their owning ledgers/consumer.

No metadata-only forced liquidation is introduced. The optimizer can later choose native contribution quantities and append real dated requests within these constraints; it must independently validate any proposed proportional tax schedule and preserve fixed contract facts. This layer does not edit optimizer menus or claim that an arbitrary supplied K-1 schedule scales with contribution value.

## User workflow and independent evidence

Products / Traditional exchange funds offers original Full contribution, Partial contribution and Retained source only profiles in the existing editable/import/export workflow. Partial/zero presets keep the original whole source lot and account capital, changing only contributed quantity and adding an explicit terminal source sale. The full source/lot/disposal audit and comparison table expose retained quantity and actual position/recognition closure. Reaching an availability date does not sell anything by itself.

Checks independently reconcile zero/400/1000-share opening splits and independent federal/NJ dollar bases, flat $130,000 household capital through actual source/basket sales and final tax, denied acceptance, source/market locks, later explicit execution and one-year holding boundaries. A prior-replacement wash case has 600 retained source shares with federal basis $110,000 / NJ basis $72,000 after a 400-share opening direct sale; a basket order leaves all source pieces intact, and the actual source order realizes the remaining recognized amounts without duplicated proceeds. A deferred supplied post-horizon allocation prevents a complete modeled-exit claim after physical liquidation. Actual Streamlit presets exercise the native calculations.

## Primary-source scope

Checked October 25, 2026. Automatic QMD `tax-references` vector discovery found the 2025 Schedule D instructions and an older 2024 Publication 550 snapshot. The actual 2025 Schedule D holding-period passage was read (PDF proof header December 11, 2025); the older snapshot was not treated as current-year proof. Current [IRS Publication 550 (2025)](https://www.irs.gov/publications/p550), Holding Period and Wash Sales, was read directly: ordinary stock trade dates determine holding periods; wash treatment can change replacement basis/holding periods and requires the stated substantially-identical relationship/window. [2025 Schedule D instructions](https://www.irs.gov/instructions/i1040sd), Short- or Long-Term Gain or Loss, supports the existing ordinary-stock character boundary. No new exception, sponsor qualification, partnership basis-allocation law or NJ wash entitlement is inferred. The no-external-trades condition and independently supplied holding starts remain explicit limits on this bounded reuse.
