# ADR 0032: Employee 401(k) investment-return schedules and market proxies

Status: further retirement/market integration for open tickets #6 and #8. Reuses actual employee election funding and existing wrapper-factor compilation; no new tax rule or dependency.

## Monthly investment boundary

The employee 401(k) plan now accepts explicit `AccountReturn` schedules and outgoing scenario restrictions. Return records must reference known classified workplace products, have resolved provenance, share unique IDs with election/lock records, and fall on a projection month end. Earlier return dates are rejected: the existing payroll book pools that month's gross wage receipts and funded employee elections and cannot support daily pricing against them.

After actual wage/limit/cash-constrained elections, each month-end return changes only the remaining workplace account balance. The existing cent-rounded return-change convention applies. It generates neither household cash nor a separate taxable distribution/wage event. Pretax wage exclusions, employee payroll, Roth wage recognition and annual election limits still use only actual funded elections. Unfilled requests earn no return. The audit separates funded deposits from investment gains/losses.

This does not permit workplace assets to fund general household spending. Existing account/product guards keep them separate from ordinary IRA pools and taxable funding sources. Outgoing restrictions remain explicit scenario inputs; incoming employee deposits and returns remain allowed. Workplace withdrawals, RMD/rollover adapters, employer matches, after-tax non-Roth contributions and excess corrections remain unfinished. A large locked balance cannot erase a cash funding failure.

## Shared paths and UI

An employee 401(k) product can use the existing full-account factor proxy, with explicit confirmation to replace its entered return schedule. The compiled copy receives the same realized monthly mark-plus-yield rates as other bound accounts. Yield stays invested; there is no extra household yield cash or inferred taxable income. Existing restrictions and unbound schedules remain intact. This is a single-factor account proxy without an inferred issuer inventory or multi-asset holdings/rebalancing model.

Markets / Household funding offers **Employee 401(k)**. The same actual payroll reconciliation appears alongside market funding outcomes, with separate investment change and a dated account audit. Household inputs can also supply manual month-end returns. Source household/binding/batch exports preserve the inputs required to reproduce the run.

## Executed checks

A synthetic 2026 employee requests twelve $2,000 pretax elections and a $2,000 December Roth election. The existing limit funds $24,000 pretax and $500 Roth, leaving $1,500 unfilled. With a 2% monthly return, the first pretax balance is $2,040; the terminal pretax balance matches an independently cent-rounded recurrence, and the funded Roth balance becomes $510. Household cash remains $176,637, federal AGI remains $96,000 and total wealth equals the original $201,137 plus actual investment change. Separate tests reject mid-month/unknown-account/unresolved returns and reused election IDs, preserve existing IRA/workplace separation and run the actual UI. A zero-cash/no-wage case retains more than $100,000 of marked workplace wealth, funds no employee election, and reports $12,000 unpaid spending.

See [employee deferral accounting](0019-household-employee-deferrals.md) and [wrapper timing/coverage](0030-wrapper-market-paths.md). All tax results retain their entered rule-year/future-law assumptions.
