# ADR 0031: Employer market factors and conditional employment linkage

Status: further integration for market ticket #8 and employment ticket #7. Reuses the supplied compensation tranche book and wage paths; no new dependency or legal classification.

## Net employer account proxy

An explicit binding maps every tranche in an employer account to one factor designated `employer`. Its marks must represent net investment performance under the existing embedded-fee convention. Separate factor cash yield must be zero: the model cannot infer payout rights, taxable allocations or reinvestment from a dividend yield. The user confirms replacing entered net-return events for the bound account. Grants, vesting, forfeiture, cash elections and supplied tax allocations remain unchanged unless the separate conditional employment rule explicitly adds a forfeiture.

At each month end, a generated net-return event applies to remaining vested and contingent pockets separately, rounded by the existing ledger. Earlier cash elections do not receive later returns. The explicit event-sequence start and successive tranche offsets determine same-date ordering; any collision with supplied events blocks validation rather than silently reordering contractual terms. Generated rates preserve twelve decimal places. Source household inputs, binding and realized batch remain exportable and unchanged; a compiled copy receives generated events.

Market locks create dated outgoing account restrictions. They block both ordinary and tax-cash elections, preserve requested/unpaid amounts, retain value and subsequent returns, and allow incoming grants. Reported redeemable/locked vested values honor the restriction at the monthly observation date. Conditional cash-right confirmations cannot override the scenario lock. These assumptions do not establish legal rights or excuse tax obligations.

## Observed drawdown and future employment

A binding may link its owner's existing, validated wage path to a first observed employer-factor price drawdown. The running peak starts at one and uses only marks observed through the current month. If the threshold is reached while the worker is active and before retirement, job loss starts on the first day of the following month. The current month's wages remain earned. Months out of work and the eventual baseline-pay multiplier are supplied. Retirement cutoffs remain effective; a return is generated only before retirement and projection end.

The user must explicitly confirm replacing manual work changes from the trigger date onward. Before that date they remain intact. A supplied option forfeits all remaining unvested value at the job-loss date; vested value remains. Its explicit sequence controls order relative to any same-day supplied vesting or grants. Later grants, vesting and taxable allocations are not inferred away. A noncash allocation can still produce tax after forfeiture or complete investment loss.

This is a conditional scenario rule, not a calibrated job-loss probability or a claim of causation. Correlated market factors come from the same existing joint batch; deterministic, historical, Monte Carlo and stress modes all use the same observed-prefix rule. A policy does not know a future price. The selected path's compiled wage changes are visible in results and export. The paired-policy form accepts either a household or a household/binding bundle, so an employment trigger or forfeiture choice can vary while the realized batch stays shared. A replacement market input in that bundle is rejected.

## Wealth, coverage and checks

Vested employer value enters ordinary marked household wealth and its known factor exposure. Contingent unvested exposure is reported separately and remains excluded from ordinary spendable/net wealth. A whole-account proxy does not disclose underlying issuers or satisfy a concentration constraint. Positive accounts without factor mappings remain visible. Net terminal wealth still is not a complete hypothetical after-tax exit value.

The Markets / Household funding account scope **Employer and employment** supplies an editable synthetic example, displays employer value/liquidity and exposes the selected path's wage changes. Existing compensation rights and source limitations remain in [ADR 0014](0014-employer-compensation.md).

Independent checks reconcile both growth pockets, actual wages, no duplicate household cash yield, unchanged supplied allocation taxes, original export preservation and factor/issuer coverage. A January 50% loss preserves $10,000 vested and $40,000 contingent value at that close. Next-month job loss forfeits the contingent amount, six months out of work followed by half-pay produces $35,000 annual wages, and the supplied $20,000 allocation still produces $55,000 AGI. Other checks cover identical-prefix/future-return independence, paired forfeiture choices, locked confirmed tax cash, mapping/confirmation guards and the actual UI.
