# 0065: One household book executes foreign tax cash before optional flows

Status: actual cash-consumer vertical of cross-border issue #17, above
[the native credit layer](0064-dated-foreign-credit-facts.md). Country-specific
residence/assessment adapters, original closed-return redetermination and
unsupported source profiles remain later work. This does not complete #17.

## Existing accounting owns the money

`Scenario.foreign_tax_plan` supplies conditional foreign assessments, dated
revisions, payment schedules, actual opening records, linked source withholding,
refund assumptions, observed USD/EUR quotes and annual US source-credit profiles.
A foreign plan requires the existing domestic tax plan. `TaxLedger` binds one
foreign cash book; `Wallet` and `fund_required` remain the only household cash
and required-sale engines. Required foreign tax executes before optional
products, wrapper deposits and liquid saving. Nullable retry callbacks between
existing receipt/product books also apply late cash, such as a real option
premium or redemption, before optional saving. The same paid/refund identities
and original remaining payable make these retries idempotent; a reentrancy
guard prevents a nested required-sale callback from starting another sale. Existing prior US tax arrears
retain their established earlier funding priority.

An assessment is not a payment. Original or revised native assessment less
actual net paid tax creates one marked payable or refund claim. Net wealth
subtracts that signed foreign position once. A refund claim cannot fund
anything before its actual supplied receipt date. An unconfirmed/denied refund
claim stays a separate contingent value excluded from actual wealth. Unscheduled
remaining assessments block a funding-success conclusion. Every observed month-end
requires a dated quote; an annual or stale quote is never substituted. USD
cash already received is not retranslated at later EUR marks.

Payments round affordable native cents down, then debit cent-rounded USD and
an explicit per-execution fee. Actual paid amounts reduce the original native
position and remaining schedule. Unfilled due tax remains debt and a required
funding failure. Extra schedules cannot duplicate the same remaining debt.
Actual received refunds preserve original payment identity and cumulative
native cash/credit caps. Receipt-date cash FX remains separate from original
credit FX; currency income needs independently recognized source facts.

A payer's foreign withholding belongs to its exact gross/net receipt and global
payment ID. `SourceWithholding` includes it in gross-minus-net reconciliation;
the foreign book records the paid assessment without another wallet debit.
Domestic paid-tax totals include only federal/NJ withholding. Foreign cash,
US income tax, employee payroll and NJ remain separate displayed measurements.
A duplicate receipt ID or mismatched payment/date/value rejects.

## Source, credit and carry ownership

Source identity is `(person, recognition year, source ID)`. Recurring labels
may persist across calendar years. An audit map retains those tuples while
stable tokens feed the lower credit engine; actual payment IDs do not change.
The payment's linked US source-income year is explicit and independent of its
foreign liability year and actual paid-method credit year. Missing source links
reject before cash mutation. No foreign source, basis, move FMV or legal
residence is derived from a US lot or household address.

A known revised foreign assessment cannot leave larger prelimited credit tax
facts silently in place; their reconciliation blocks the affected credit until
its supplied facts/cash reversal support the new amount.

The current derived standard-deduction profile requires entered state deduction
facts. Actual-payment deductions changed during post-credit settlement need a
separate allocation/reconciliation profile; they cannot retain a stale claim.

Denied US credit does not erase unknown foreign source or basis facts: source
rows must still reconcile, and unclassified capital/retirement/business amounts
remain unsupported.

The book clears only its owned US credit before recalculation. Actual paid tax
feeds native federal credit order; quotes cannot spend an anticipated credit or
refund. A later product/funding event must reconcile to recognized source facts
before its favorable credit can remain. A real US lot sale still executes
through existing basis/wash/tax accounting, but missing foreign gain/source/basis
makes the cross-border result unsupported. The now-known domestic bill is
funded through the existing required-sale solver after clearing stale credit;
no additional foreign liability is invented.

Each new year derives original carry vintages from actual prior annual use,
not from the last monthly snapshot and not from another opening input. The
same original opening capacity is evaluated against current YTD facts without
consuming it again each month. Prior carryback review and joint-person excess
allocation remain requirements; unresolved disposition blocks a favorable
future claim. Denial never refreshes a vintage's age or creates refund cash.

## UI, evidence and boundaries

Cross-border / **Household foreign taxes** edits the real household JSON,
executes `project`, shows the ordinary household cash/wealth view plus foreign
positions/payments/credits, and exports inputs/audit. The ordinary Household
form and synthetic example use the same plan and engine. Invalid edits clear
stale results. The public examples contain supplied synthetic assessments,
not a claim that Spain or Puerto Rico has assessed that tax.

Primary credit/currency authorities and final2025/frozen2025 limits remain in
ADR0064. This cash bridge does not create additional legal eligibility. Pure
PR/Spanish assessment engines must eventually supply independently classified
liabilities, stable person/year/source/payment IDs and confirmed remaining
obligations. Unknown legal or foreign gain/basis facts appear in
`foreign_tax_unresolved`, invalidate household funding success and must not
rank as a supported optimizer outcome. Country residence, part-year NJ,
Spanish/PR credit ordering, preferential/AMT credit allocations, unsupported
foreign product classifications, original-year US redeterminations and general
native-currency bank-account/section988 accounting remain explicit gaps.

Independent checks reconcile an actual $11,000 payment with a separately capped
$6,724.50 US credit. A $7,000 wallet pays EUR6,363.63 / $6,999.99, retains $0.01
cash and $4,000.01 marked debt. A payer's $20,000 gross/$11,000 foreign tax
leaves $9,000 cash, with only $1,530 additional domestic payroll debited; induced
AMT remains unsupported instead of receiving an implicit AMT credit. A reduced
assessment creates a $1,400 claim before receipt, later returns $1,400 cash,
reverses $1,100 credit tax and recognizes a separately supplied $300 currency
amount without another receipt. Required $11,000 tax leaves $39,000 of the same
$50,000 opening capital for optional shares. Multi-year checks preserve the
$4,275.50 original2025 excess into one2026 claim and keep recurring source labels
separate by person/year. Real funding-sale tests preserve exact US taxes while
blocking absent foreign basis/source, and generic Household/Cross-border UI
checks exercise the actual consumers rather than isolated illustrations.

A partial payment can use a later actual receipt in the same month. Each real execution has its own deterministic payment ID and retains the original schedule ID; the first execution identity remains compatible with supplied refund links. Repeated retries without new cash or after full payment add no debit. Generated identities cannot replace reserved opening/withholding/refund IDs, and each actual execution retains its separately disclosed fee.
