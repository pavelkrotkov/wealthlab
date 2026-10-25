# 0046: Net receipts and source-withheld income tax

Status: accepted. Source checks: October 24, 2026 (New York).

## Problem and decision

An external payer can remit income tax before depositing the net distribution.
Entering only the net receipt loses the tax credit. Entering gross cash and a
later estimated payment lets optional wrapper deposits spend money the payer
already withheld. Neither represents the actual cash flow.

`TaxEvent.withholding` optionally supplies `gross_cash`,
`federal_income_withheld` and `nj_withheld`. Nonnegative amounts must reconcile
exactly: `cash_received = gross_cash - federal_income_withheld - nj_withheld`.
Income character and taxable amounts remain separately entered: gross cash can
include a return of basis. Absence preserves existing event behavior.

The common recognition helper credits existing annual Payments. The household
receives only net cash; there is no second wallet payment. Actual-payments mode
adds source-paid NJ income tax to the existing federal state-tax deduction;
entered mode leaves the entered deduction unchanged. Scheduled wage withholding
remains a separate election. Source credits do not cancel an explicitly elected
wage deduction; existing year-end settlement reconciles all actual payments.

Plan events, extra events and both receipt hooks share this implementation.
Monthly `tax_source_withholding` and individual `tax_source_receipts` expose
actual payer remittances. Reported gross cash taxes include these once, alongside
wallet-paid taxes. Existing annual balances, jurisdiction-specific refund
receivables, receipt dates and return revisions continue to govern wealth and
liquidity. Opening YTD payments are not redeposited or counted as current source
receipts. Future annual cases still prohibit opening payments.

## Sources and limits

The [IRS 2025 Form 1040 instructions, line 25b](https://www.irs.gov/instructions/i1040gi)
direct taxpayers to report federal withholding from Form 1099-R box 4 as a
payment. The official page was checked directly; local tax-reference vector
search identified the 2025 instructions but its returned index passage did not
support the rule. This feature accepts supplied actual/conditional payments;
it does not infer legal withholding rates, pension basis, plan eligibility,
withholding elections, filing deadlines or a new tax regime. Existing annual
law settings and conditional NJ treatment remain explicit.

## Executed checks and UI

The Household loader **Load synthetic pension with source withholding** supplies
an original synthetic $10,000 gross pension, $2,000 federal withholding and
$8,000 net receipt, with an $8,500 personal HSA request. Only $8,000 funds the
HSA; no scheduled tax payment is missed. With this example's zero final
liability, the $2,000 credit stays a receivable until the following April.
Wealth remains $10,000 throughout, while available cash remains zero until
refund receipt. The tax JSON form and scenario import/export preserve the
record; the UI displays gross cash, net cash and each jurisdiction's tax.

Checks cover malformed reconciliation, return of basis, entered versus actual
NJ deductions, all four event routes, monthly reset versus annual credit carry,
December/January deduction boundaries, actual delayed refund cash, household
wealth, matched tax reporting and the submitted UI.
