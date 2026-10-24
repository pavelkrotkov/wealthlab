# ADR 0027: Actual household funding on realized market paths

Status: a further integration layer of open market ticket #8. Reuses [realized batches](0024-paired-market-paths.md), [actual taxable lots](0025-household-lot-funding.md), [January reconciliation](0026-january-wash-reconciliation.md) and the existing household tax/payment ledger. No new dependency or relaxed gate.

## Same household, same batch, actual cash

An execution binds every linked taxable security exactly once to an existing market factor. Every scenario and batch horizon must match. Each selected path compiles opening prices into month-end marks, rounded to the lot engine's eight decimal price precision. Actual permitted funding trades use those observed marks, existing lot selection, separate bases, commissions and cash tax funding. Future marks cannot choose an earlier sale. Source scenario and realized arrays remain unchanged.

Separate monthly cash yield is received on the opening marked value of shares actually remaining at the start of that month. The entered ordinary federal and NJ dividend/interest/exempt characters feed the same return once; no qualification or issuer calendar is inferred. This monthly convention requires confirmation. Yield is cash, not extra share appreciation, reinvestment or basis. Taxable reinvested-total-return marks are rejected because their missing distributions/basis would hide taxes.

A supplied factor liquidity lock prevents that security's funding sales while retaining its marked wealth. Existing date-specific lot locks also remain. Other permitted sources can meet the gap; otherwise spending/tax shortfalls remain visible. An unobserved terminal wash window uses only the explicitly selected assumption from ADR 0026.

## Inflation and scope

Only selected zero-growth expense streams use realized prior-month CPI. Month one uses opening purchasing power; the month's inflation affects following spending and current end-of-month real reporting. Other expenses, wages, debt contracts and wrapper schedules retain entered nominal/growth assumptions. Market CPI does not silently index tax law, contribution limits, benefits or Medicare premiums. Other accounts' unmodeled market returns require confirmation. Generated employment and benefit cash still comes from the prepared household, not the unprepared source copy.

The initial binding profile executes actual taxable funding with ordinary cash yield. Manual dated trades need a market execution-price adapter and are rejected; automatic sale/harvest/rebalance policies, qualified issuer distributions, account fee adapters, wrapper/employer factor binding, linked job loss and spending guardrails remain unfinished. Zero-price/delisted marks require a write-off adapter and block instead of leaving a positive placeholder. Marked terminal wealth includes unrealized gains; this is not a complete after-tax liquidation value.

## Outcomes and pairing

Every path reports actual supplied-horizon funding, first failure, new obligation shortfall, missed tax schedule months, cash reserve breaches, peak-to-trough net-wealth drawdown, maximum individual-security weight, terminal nominal/real wealth and tax position. Reserve breaches compare actual cash with the entered reserve target. Net-wealth drawdown includes spending and external flows; concentration divides security value by total gross household assets, not net equity after debt.

Monte Carlo results include a two-sided 95% Wilson interval for the fraction of simulated paths funded under this model. This describes sampling error, not market/tax model error or a calibrated probability. Deterministic, historical and named stress outcomes do not receive a sampling interval. [NIST/SEMATECH 7.2.4.1](https://www.itl.nist.gov/div898/handbook/prc/section2/prc241.htm), checked October 24, 2026, supplies the formula. The age-coverage diagnostic requires the horizon to cover the entire specified age of the younger person; a short example cannot establish safety through age 100.

Paired policies require identical batch identity and ordered path indices; otherwise comparison blocks. The UI uses a user-bounded prefix of the generated batch and shows workload before execution. Export contains original household, bindings, realized batch, indices, outcomes and actual ledgers. Historical examples disclose invented mathematical observations and synthetic retrieval dates; no downloaded market data is redistributed.

## Independent checks

A flat $100,000 stock holding with $2,000 monthly ordinary cash yield receives $48,000 over two years. With no wages/spending, federal ordinary dividends are covered by the standard deduction; NJ gross $24,000 less $2,000 exemptions incurs $315 per year. Opening wealth $101,000 plus $48,000 receipts less $630 taxes ends at $148,370, with unchanged shares and basis.

Checks also execute a two-year liquidity lock, matched spending policies using indices 0 and 2 of one seeded batch, prior-CPI spending, no changed earlier sales from a last-month crash, invented historical replay, all named stress inputs, explicit binding guards and the real Markets / Household funding form. Completed-return, January, actual-lot and existing household checks protect the reused ledger.

The household runner also validates actual batch dates and every array axis against the household horizon before selecting paths. Direct Python batches cannot use metadata alone to hide missing observations; malformed axes fail with a user-facing error. Validated historical inputs independently reject an extended horizon without matching observations before generation.
