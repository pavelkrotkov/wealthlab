# 0050: Confirmed incoming plan cash shares the annual IRA book

Status: accepted; a primitive for open retirement ticket #6. Source checks:
October24,2026 (New York). Household source debits remain a separate adapter.

## Result and accounting

Retirement / IRA withdrawals adds **Direct plan rollover with withdrawals**.
An optional `incoming_rollovers` list represents actual, eligible direct cash
receipts from an external ordinary qualified plan into a same-owner traditional
IRA. Required confirmations exclude source RMDs, inherited/designated-Roth or
other special features, duplicate opening assets and duplicate cash receipts.
This is a funded receipt, not an instruction to request an uncertain transfer.
Destination identity, owner, date, provenance and event IDs are validated.

The existing IRA timeline applies incoming plan cash before same-day returns
and withdrawals. It increases the destination once, without increasing spending
cash, using regular contribution room or generating an IRA deduction. A future
receipt cannot finance an earlier failed withdrawal. Existing outgoing locks
still restrict withdrawals; they do not imply a custodian rejects incoming cash.
An incoming rollover does not carry the source plan's separation-age exception
into an IRA withdrawal.

Federal and NJ transferred basis are required independent supplied amounts.
The adapter does not compute a source plan's pretax/after-tax allocation or
assume state basis equals federal basis. This cash profile rejects supplied
transferred basis greater than receipt value rather than silently capping it.
Annual owner-wide basis reconciliation includes actual transferred basis,
including its effect on earlier distributions in that tax year. Receipt-date
asset availability and annual basis aggregation therefore have different timing.
Opening prior-December values remain the IRA RMD denominator.

Ordinary IRA deposits retain their separate actual cash funding, annual room,
compensation/MAGI and deduction checks. Incoming rollover IDs also cannot
collide with their cash events. The result exports actual receipts and separate
basis; the UI labels received IRA assets independently from spendable cash.
No inferred withholding, deduction, taxable receipt or tax-savings cash is added.

## Reproducible checks

An original synthetic IRA starts with $10,000 and federal$1,000/NJ$2,000 basis.
It receives $20,000 with independently supplied federal$4,000/NJ$6,000 basis,
then withdraws $15,000. It ends with $15,000 IRA assets and $15,000 cash before
income-tax payments. The withdrawal recovers federal$2,500/NJ$4,000, recognizes
$12,500/$11,000 income, and carries $2,500/$4,000 basis. Without withdrawals,
received value creates neither cash nor incremental tax liability.

Checks cover independent basis, conservation, repeated runs, same-day return
ordering, a later receipt, liquidity, IRA penalty age, unchanged prior-December
RMD base, ordinary contributions, invalid destination/owner/year/provenance,
missing eligibility confirmations and the submitted workbench UI.

## Sources and scope

QMD tax-reference discovery returned general Form1040 instructions without a
supporting source-allocation passage; those hits were not treated as proof.
[IRS Publication590-A (2025)](https://www.irs.gov/publications/p590a), rollover
sections, distinguishes direct plan transfers, ineligible RMDs and ordinary
contribution deductions/limits. [Publication575 (2025)](https://www.irs.gov/publications/p575),
rollovers of after-tax amounts, states that after-tax amounts rolled into a
traditional IRA become IRA basis. [IRS after-tax rollover guidance](https://www.irs.gov/retirement-plans/rollovers-of-after-tax-contributions-in-retirement-plans)
describes source allocation and multiple destinations; this layer requires
already-confirmed transferred basis rather than implementing that allocation.
[NJ retirement bulletin, January2026](https://www.nj.gov/treasury/taxation/pdf/pubs/tgi-ee/git1%262.pdf),
printed pages9/14, distinguishes untaxed traditional rollovers from later
state-taxable pension withdrawals and independent cost recovery. Existing IRA
aggregation and frozen-year assumptions remain those of ADRs0006/0020.

In-flight or 60-day transfers, source allocation, designated Roth, inherited
products, partial destinations and basis greater than value need their own
validated profiles. This annual workbench does not debit a modeled household
plan, fund income tax, perform a trade or establish household retirement safety.
The next household adapter must debit the actual source before supplying this
receipt, preserve source RMD exclusions, and rebuild the IRA's dated balances;
a wallet-only credit would be overwritten by its existing schedule.
