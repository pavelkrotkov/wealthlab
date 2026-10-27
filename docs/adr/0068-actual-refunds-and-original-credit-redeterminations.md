# 0068 — Actual refunds and original credit redeterminations

Status: accepted implementation boundary; ordinary paid-method profile.

## Decision

Observe actual refunds in the existing foreign-tax book, then reuse `return_reconciliation.apply_revision` against the actual closed US returns. Preserve the public January-only revision guard for other callers. This consumer separately validates the actual later-refund profile and its observation date. It creates no second wallet or tax engine.

The original US **paid-tax year**, not the foreign liability year, owns the credit correction. A foreign 2024 assessment paid in 2025 and refunded in 2027 revises the actual US 2025 return and affected subsequent carry years. Original foreign payment cash, date and FX remain immutable. Only the revised credit facts reduce original creditable native tax for actual later refunds. The receipt is not backdated. Same-year refund rows remain in their original cash history.

Recompute affected original years in order using their actual native annual facts and original carry vintages. Validate on copied position/credit books before committing any change. A blocked later carry year cannot partially amend the earlier original return. Missing actual original returns, provisional source facts, unresolved carry disposition and unconfirmed treatment block the affected revision while actual refund cash remains visible. Unknown incidental costs do not erase known US principal: native arrears are still paid, while the overall funding result remains blocked until cost assumptions are complete.

The native reconciliation preserves actual tax net paid, adjusts outstanding liabilities and delayed refund queues, and leaves original payment inputs intact. The existing native prior-tax payment function pays new US arrears before optional products/contributions. Retried callbacks use the observed refund IDs and current outstanding balance; they cannot debit the refund twice. Domestic principal paid is reported as native prior US tax, separately from foreign cash and employee payroll.

The original quote translates the credit reversal. Receipt-date cash and separately classified receipt-year currency income retain their own date and source. Negative FX losses, unsupported AMT/preferential/treaty allocations and missing source classes remain guarded. Interest, penalties and compliance costs require independently supplied existing dated expenses, or an explicit confirmed zero-cost assumption. The model does not infer an interest exemption or generate a filing/payment date from related guidance.

Export a canonical final source-return map from the actual closed-return book after terminal wash/product reconciliation. It includes actual net paid, owed/receivable positions, final native liability and provisional status. Separate revision histories remain intact; sorting them is not used to infer the latest return.

## Primary authority and verification

Final [Publication 514 (2025), pages6–8](https://www.irs.gov/pub/irs-prior/p514--2025.pdf), dated January 30,2026, distinguishes original-credit redeterminations from additional prior-liability taxes newly paid under the paid method. Its notification discussion requires affected-year revised Form 1116 facts, original payment and refund quotes, and information about interest. The [IRS HTML edition](https://www.irs.gov/publications/p514) was rechecked October 25,2026. Final [2025 Form 1116 instructions, page3](https://www.irs.gov/pub/irs-prior/i1116--2025.pdf) retain the original translation for refunds. These sources support this bounded cash-method/refund consumer; they do not establish treaty, AMT or preferential-income eligibility.

Automatic local tax-reference vector discovery was followed by reading source headers and supporting passages. Older 2024/2023 Publication 514 mirrors, 2018 Form 1116 instructions and a 2022 regulations bulletin were excluded as current individual-form authority. No private taxpayer record or local source-library path is published.

Checks execute a EUR 5,000 refund at 1.40 as USD 7,000 cash; original 2025 FTC falls from 6,724.50 to 5,500, and 4,275.50 used in 2026 is reversed. Existing native US settlement pays 5,500 before optional saving, leaving 1,500. With a separately supplied 250 expense, only 1,250 is saved. The FX 1,500 stays receipt-year income. Other checks cover foreign liability year versus paid year, unchanged original payment inputs, native actual net-paid positions, atomic rejection, uncertainty, zero-outstanding retries and the editable UI/export lifecycle.

This layer does not claim universal issue 17 completion. General one-year carryback computation, native preferential gains/basis, treaty resourcing, independent AMT allocations, independent NJ prepayment/refund positions and later country-assessment revisions still require their supported adapters.
