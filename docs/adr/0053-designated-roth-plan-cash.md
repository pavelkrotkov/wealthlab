# 0053: Ordinary designated Roth plan cash retains its own contract cost and clock

Status: accepted; bounded retirement ticket #6 layer. Source checks:
October24,2026 (New York). NJ treatment remains an explicitly entered assumption.

## Result

Household adds **Load synthetic designated Roth plan cash**. Optional workplace
`roth_cash_withdrawals` contains complete ordinary vested Roth401(k) contracts,
their logical subaccounts, separation date, independent federal/NJ opening cost,
first federal participation year and first-day cash orders. Each classified
Roth source appears in exactly one contract, with one owner. Unknown opening
history, duplicate coverage, unresolved orders and special features block the
profile before cash moves. In-plan conversions, inherited products, loans,
NUA, hardship, excess corrections and direct Roth rollovers require other
profiles; their tax consequences are not inferred.

The existing actual workplace assets, outgoing locks, monthly payroll, returns
and source tax-payment ledger are reused. Cash precedes funded employee
elections and month-end plan returns. Only actual available source assets are
paid; failed optional requests are audited without retry. Subaccounts share
the complete contract's value when calculating the pro-rata cost fraction.
Federal and NJ cost are separate pools. Actual funded Roth payroll adds taxed
principal to each pool and can establish a previously absent participation year;
forecast eligibility without current wages creates neither principal nor clock.
Deferrals after the source's confirmed separation date are rejected.

Federal ordinary qualification requires both five completed taxable years and
age59½. Nonqualified cash recognizes its earnings share; qualified cash has no
federal taxable income but still consumes proportional cost. Age55 calendar-year
separation can exempt otherwise early taxable earnings from the additional10%
tax; it does not turn the payment into a qualified Roth distribution. Existing
half-birthday logic supplies the exact age boundary. Owner-lifetime RMDs are not
created for this designated Roth profile.

Required NJ fields explicitly confirm the conditional same-qualification and
pro-rata-cost scenario with independently supplied NJ cost. The UI, audit and
export retain that assumption; it is not a conclusion that NJ eligibility was
verified from federal status. The federal and NJ tax adapters receive their
separate actual recognized pension amounts. Federal withholding uses the
eligible payment's taxable portion, with at least20%; NJ uses its separately
entered rate on the conditional NJ taxable portion. Only net cash reaches the
household; source credits and delayed refunds use the existing payment ledger.

## Losses and reporting boundary

Cost can exceed current value after market losses. Recovery never exceeds
actual paid principal or remaining cost, and taxable earnings cannot become
negative. Unrecovered cost in an empty separated contract remains visible in
its cost audit, without becoming a wallet asset, deduction or tax-saving cash
receipt. This profile does not reopen the source through later deferrals.
Actual cash-loss deductibility is outside the modeled tax profile; historical
rulings are not silently applied as current deductions. Remaining value, cost,
participation year and state assumptions are shown even with no cash order.

## Reproducible evidence

The original synthetic contract has $10,000 value, federal$9,400/NJ$9,000 cost.
A $5,000 nonqualified payment recovers $4,700/$4,500, recognizes $300/$500,
withholds $60 federally and receives $4,940 cash. Separation occurred at54;
$30 additional federal tax applies. The synthetic joint tax context has no
other final liability; the $30 excess withholding refunds next April. Ending
wealth is $9,970, including the remaining $5,000 source value.

A qualified $12,000 payment from $23,000 value with $21,850 federal cost consumes
$11,400 cost, leaving $10,450 cost and $11,000 assets; federal taxable income is
zero. Other checks cover exact59½/five-tax-year boundaries, age55 access,
logical subaccount pooling, independently supplied NJ cost, losses, locks,
no retry, actual/new payroll cost and clocks, invalid history/source identity,
ordinary owner-lifetime RMD exclusion and the submitted Household form.

## Dated primary references and limits

Automatic QMD tax-reference discovery returned ordinary IRA/general1040
passages rather than designated Roth plan authority. Those rankings were not
used as proof. [Current26CFR1.402A-1](https://www.ecfr.gov/current/title-26/section-1.402A-1),
Q/As3,4,7,9, distinguishes the ordinary nonqualified allocation, participation
period, cost remaining after qualified cash, and one contract per employee/plan.
[IRS Publication575 (2025)](https://www.irs.gov/publications/p575) covers designated
Roth cost and ordinary nonperiodic distributions. [Notice2026-13 in IRB2026-06](https://www.irs.gov/irb/2026-06_IRB)
supplies current rollover explanations, taxable-earnings withholding and the
section402A(d)(5) lifetime-RMD change. [The2024 final RMD regulations](https://www.irs.gov/irb/2024-33_IRB)
exclude designated Roth amounts from the owner's lifetime denominator. Older
IRS topic-page statements about lifetime Roth-plan RMDs were not used.

[NJ GIT1&2, January2026](https://www.nj.gov/treasury/taxation/pdf/pubs/tgi-ee/git1%262.pdf)
distinguishes state pension cost, but the consulted text does not establish
this specific designated Roth qualification profile. NJ's separate Roth IRA
paragraph is not substituted for plan authority. The explicit conditional NJ
profile preserves this limitation instead of silently assuming conformity.
[The2007 final Roth regulations](https://www.irs.gov/irb/2007-22_IRB) separately
discuss cost greater than value and full-account rollover/cash-closure contexts;
their reference to a historical loss ruling does not establish a current modeled
deduction. This feature is ordinary separated plan cash, not a direct Roth
rollover, disability/inherited engine or complete retirement optimization.
