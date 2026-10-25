# 0100: Audit supplied whole-life illustrations before applying contract assumptions

Status: first vertical layer of issue #14, October 25, 2026. Contract tax,
actual household premium funding, liquidation/lapse and a matched liquid-saving
plus separately priced protection comparison remain required follow-on work.
This layer does not close the whole-life ticket.

## Inputs and interpretation

Products / **Whole-life illustrations** accepts a `LifeStudy` JSON document with
separate guaranteed, current and stressed illustrations. Each contains source
metadata, issue date, funding-path description, limited-pay/long-duration/custom
premium classification, optional last premium date, actual dated external cash
flows and supplied gross cash, surrender and death values. The study contains an
optional retirement date and insurance need; neither is inferred from wealth.
Public examples use invented small-dollar schedules and represent no insurer.

A value is measured after every flow on its date. Loan advances are cash receipts
and liabilities; principal repayments reduce both cash and debt. Explicitly paid
interest is a cash outflow. Capitalized interest increases debt without creating
a cash flow. Embedded charges and retained dividends already affect the supplied
values; only external fees and actual cash dividends are entered as cash flows.
All gross values are before outstanding loan debt. Policy cash value, surrender
value and death benefit are alternative terminal measurements, never additive.
The audit shows loan debt and each net value separately.

A supplied history must cover issue onward and be confirmed complete before
opening debt is assumed zero. The user must also confirm that the values match
the selected cash-flow/funding path. Unconfirmed paths retain raw supplied data
but produce no derived net values or returns. Missing values stay null. If
positive debt reaches known cash value, or cash value is unknown while debt is
positive, net values/IRRs are withheld and a contract-review flag is set. This
cannot establish actual lapse, an overloan rider, grace period or in-force status.

The stop-funding date validates a separate supplied path; it does not delete
premiums and leave old illustrated values unchanged. Values after stopping
funding require a new supplied illustration, including any reduced paid-up or
surrender consequences. The starter deliberately shows an unknown stop-funding
path. Future premium totals from the retirement date remain separate from the
insurance-need shortfall; this audit does not claim those premiums are affordable.

## Dated returns and reuse

Use the already pinned QuantLib 1.44 `CashFlows.npv`, Actual/365 Fixed day count
and Brent solver, rather than another financial library or a custom root solver.
The solver works in continuous-rate space and converts with `expm1` to an annual
effective return. This avoids the -100% annual-rate boundary during bracketing.
Same-date flows are aggregated first. A unique conventional IRR is reported only
for one negative-to-positive cash-sign transition; more complicated borrowing
and later premium patterns can have multiple roots and retain an explicit
unknown-return status. Values and cash ledgers remain visible in those cases.
Dates outside QuantLib's 1901–2199 range, solver failure and nonfinite roots also
produce an unknown status. Returns are before tax and do not substitute a
policy dividend interest rate for investor cash-flow return.

The [pinned QuantLib NPV source](https://github.com/lballabio/QuantLib/blob/v1.44/ql/cashflows/cashflows.cpp)
provides the dated discount calculation. An executable check found the convenience
`CashFlows.yieldRate` solver did not converge for -$1,100 / +$1,210 one year apart
in the installed build; the NPV/Brent adapter returns 10%, also verified for
small amounts, negative returns and a leap-year interval.

[lifeLib's reference whole-life model](https://lifelib.io/libraries/uslib/products/whole_life/product-spec.html)
was examined before implementation. It supplies representative actuarial contract
mechanics and assumptions, not the user's actual illustration. Replacing missing
policy terms with that representative contract would invent guarantees and loan
rules. We therefore retain the supplied-path boundary and do not add lifeLib or
modelx as dependencies for this layer.

## Import, UI and checks

JSON preserves all metadata and controls. CSV has a fixed exported header and
separate flow/value rows keyed by illustration ID. Import replaces the complete
schedule for each case/type present, preserves other schedules and rejects
unknown cases, mixed row fields, malformed rows, duplicate IDs/dates, out-of-order
flows and invalid date horizons. Blank value cells remain unknown. CSV import
clears the correspondence confirmation for every affected case; the user must
review and reconfirm the match. Inputs, schedules and the complete audit can all
be exported locally. Invalid form submission clears the previous result.

Independent checks include -$1,000 / +$1,100 over 365 days = 10%; a 366-day
interval = `1.1 ** (365/366) - 1`; separate cash/surrender/death alternatives;
external fees and cash dividends; loan principal, capitalized interest and
repayment conservation; ambiguous IRRs; unknown stop-funding values; CSV import
isolation; and the actual editable Streamlit form. These do not validate an
insurer's supplied values or establish household funding safety.
