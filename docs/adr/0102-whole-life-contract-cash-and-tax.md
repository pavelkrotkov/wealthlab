# 0102: Executed policy cash, separate loan debt and conditional income tax

Status: second vertical layer of issue #14, October 25, 2026. Actual household
premium funding, failed-premium continuation, spending reserves and matched
liquid-saving plus separately priced protection remain required. This page
accepts events as already executed and funded; it does not close the ticket.

## Contract and accounting boundary

Products / **Whole-life contract cash and taxes** accepts a supplied opening
snapshot and dated executed events. Opening federal investment in the contract
is an independent input, including any previously taxed-loan adjustments; it is
not inferred from cumulative premiums or net cash value. Opening loan debt is
separate. Same-day events retain their entered order. Supplied cash/surrender/
death values follow all events on their date and require confirmation that they
match this executed path. Unknown values and loan-exhaustion warnings use the
existing illustration guard; no insurer valuation or automatic lapse is inferred.

Premiums increase investment and consume cash. Cash dividends and withdrawals
are receipts. Loan advances increase cash and debt together; capitalized interest
increases debt without cash. Principal repayment reduces debt and cash, without
being a second premium. Paid interest and external fees consume cash and create
no automatic deduction or basis increase. Embedded charges are already reflected
in supplied values. Future loan interest must be supplied as dated amounts; this
layer does not invent rates, accrual conventions or capitalization terms.

A surrender or explicitly confirmed lapse supplies gross settlement before loan
satisfaction. Net received cash is gross settlement less outstanding debt; the
policy then closes with no remaining asset or debt. A settlement below debt is
rejected because cancellation and nonrecourse assumptions need a different tax
profile. Later policy events and supplied in-force values are rejected, so a
closed policy cannot reappear. Stopping premiums requires a corresponding supplied
path and last-premium date, as in the illustration layer. The date does not create
paid-up status. Actual premiums from the independently supplied retirement date
are reported separately from affordability and insurance need.

## Conditional federal profile

The supported profile is an ordinary personal life contract under section7702,
with separately confirmed MEC/non-MEC status, no aggregation or special historical
basis adjustments, and supplied complete opening investment. Seven-pay testing,
material changes, transfers, exchanges, employer-owned/qualified policies,
accelerated death benefits and annuitization are not inferred. Unconfirmed contract eligibility also blocks tax conclusions for premium-only
histories; the absence of receipt income does not establish section7702 status.
Unconfirmed classification or investment propagates unknown taxable amounts and basis;
subsequent premiums cannot repair unknown history.

For non-MEC ordinary withdrawals/cash dividends, cost is recovered first only
when the absence of early benefit-reduction recapture is confirmed. Ordinary
loans are not recognized on advance. MEC receipts use income first, measured
against supplied pre-receipt cash value **before surrender charges**. Deemed loan
income increases investment by the included amount; the untaxed loan portion
does not consume investment. Capitalized interest follows this rule only when
its treatment as a new loan is explicitly confirmed. Full surrender/lapse
recognizes positive gross settlement less remaining investment; a personal loss
is not deducted. The separate 10% MEC additional tax applies before the owner's
59½ date unless a qualifying disability or substantially equal-payment exception
is explicitly confirmed. No exception eligibility or later recapture is inferred.

These rules use [26USC72(e)(3)–(6), (10), (12) and (v)](https://uscode.house.gov/us/usc/119-120/t26/s72/),
text through October7,2026, and the early-reduction boundary in
[26USC7702(f)(7)](https://uscode.house.gov/us/usc/119-120/t26/s7702/).
[IRS Publication525 for2025](https://www.irs.gov/publications/p525) identifies
ordinary surrender reporting. The unchanged surrender example in
[Revenue Ruling2009-13, Situation1](https://www.irs.gov/irb/2009-21_IRB)
provides an independent $78,000 settlement / $64,000 investment / $14,000 income
oracle; the ruling's secondary-sale examples are not implemented here.

## Annual engine reuse and independent NJ assumptions

Each supplied annual baseline is evaluated before and after recognized policy
income, including years with no events. Event years without a baseline remain
visible as recognition-only results. An unconfirmed contract profile withholds
annual conclusions even when no event occurs. New federal insurance-income and additional-tax fields remain separate
from ordinary pension and retirement additional-tax inputs. Tax-Calculator6.8.5
maps policy income to the ordinary taxable-pension/annuity return line, but its
NIIT kernel omits life-contract income. Reuse that same public `NetInvIncTax`
function with existing investment components, completed AGI and capital netting,
adding policy income only to the isolated NIIT invocation. Its temporary interest
carrier never enters a second full return calculation, EIC, QBI, payroll or other
credits. Only the NIIT difference adjusts total income tax after credits. All
record arrays are fresh and evaluation retains the existing process lock.

[IRS2025 Form8960 instructions, line7](https://www.irs.gov/instructions/i8960)
include taxable life-contract disposition gains in investment income; ordinary
qualified retirement distributions remain excluded. This adapter retains the
existing kernel's disclosed investment-expense, foreign-income and other return
coverage limits. Future years use the existing explicit tax-law assumptions.

NJ recognition is independently supplied per receipt/loan/termination event and
mapped to ordinary Other income, with no pension exclusion. The available
NJ1040 material did not establish a validated general living-policy rule, so
missing state treatment stays unknown rather than inheriting federal investment
or MEC treatment. A tax year with any unknown federal or NJ recognition produces
no combined annual tax conclusion. A missing annual baseline reports recognized
amounts only. Annual baselines are independent and do not propagate carryforwards.
Tax changes are liabilities; this page executes no payment, refund or tax-saving
cash receipt. The household consumer must use its existing tax reconciliation.

## Verification and local UI

JSON input preserves source dates, assumptions, executed events and annual cases;
JSON audit/input and CSV event-ledger exports remain local. The actual Streamlit
form exposes unknown treatment, rejects invalid histories and clears stale results.
Checks cover cost-first withdrawals, MEC income-first ordering, taxed-loan basis,
repayment, capitalized interest, a zero-cash taxable lapse, statutory age boundary,
independent NJ recognition, missing values and closed-policy resurrection. The
annual adapter checks MAGI-limited NIIT, capital-loss netting, additional-tax
accumulation, low-income credit isolation and repeated-evaluation isolation.
