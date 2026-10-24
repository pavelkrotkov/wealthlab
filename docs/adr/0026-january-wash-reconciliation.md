# ADR 0026: January observations finalize original-year wash losses

Status: an opt-in extension of [actual household lots](0025-household-lot-funding.md), within open market ticket #8 and retirement ticket #6. The default remains to block unresolved December windows. No new dependency.

## Original-year recognition, unchanged historical cash

`year_end_wash_policy: january_reconcile` permits full-calendar-year household projections to carry an unresolved December loss provisionally. Unresolved loss remains excluded from that return. Actual January purchases update the same wash book and replacement basis; after the forward window closes, the recognized difference amends the original year's annual case. It never becomes January capital income. Partial replacements defer only the matched loss. Separate federal/NJ bases and the expressly conditional NJ wash choice remain in force.

Closed returns retain original payment inputs and a separate source-year net-paid ledger. Subsequent arrears payments increase that ledger; actual refunds decrease it. The corrected liability changes remaining tax owed/refund receivable, not cash already spent or received. Newly known refunds follow the configured receipt month, pushed to the following month when that date has already passed. A revision cannot deposit a January refund before January's observation. State-refund tax-benefit recovery keeps its existing explicit fraction requirement; an unsupported recovery blocks before position mutation.

The January correction updates the current year's opening capital carries before that month's recognized events finish. December cash rows stay historical and visibly provisional. The annual UI separately shows the finalized original-year return and a dated correction table; its return payment balance is distinguished from later actual cash.

## Completed wrapper context

Funded IRA elections are checked after the original-year loss resolves, even when replacements leave total recognized gains unchanged. Excess Roth contributions or overclaimed deductions block the result. Actual posted deduction/nondeductible elections and associated basis stay fixed: a subsequently larger allowed maximum is not silently claimed and basis is not retroactively rewritten. This explicit profile also accepts otherwise deductible contributions designated nondeductible. Existing unsupported Social Security/passive-loss MAGI worksheet guards remain.

Corrected federal AGI replaces the generated household return record for future Medicare lookbacks; historical bills and payments remain unchanged. Already billed conditional redeterminations require a billing adapter and are rejected. Qualified household education audits use corrected NJ gross income and actual funded NJBEST contributions. These changes do not infer additional eligibility or introduce unsupported wrapper distributions.

## Terminal information boundary

A final December loss without following January observations still blocks unless `post_horizon_purchases: none_for_30_days` is explicitly selected. That conditional assumption closes the wash window after the horizon, checks the fixed IRA election, and updates terminal tax positions and wealth. It adds no future refund to spending cash. Unused capital losses remain carry, not a refundable asset. The UI labels this assumption. Full-calendar horizons, complete outside-purchase/ownership context and existing linked-lot validation remain required.

## Evidence and executed checks

The synthetic UI case sells ten high-basis shares for $500 in December: federal loss $400 and NJ loss $300. With no January replacement, federal AGI changes from $60,000 to $59,600; a $48 refund receivable is paid in April. January cash equals December cash. Ending shares plus cash total $280,713. A January replacement defers all $400; a four-share replacement defers $160 and permits only $240, producing $28.80 federal refund cash.

Real-ledger checks independently cover paid/unpaid revised tax, already received refunds, early receipt assumptions, guarded/confirmed state-refund income, original-year recognition, partial replacements, terminal carry/assumptions, Roth eligibility under both replacement outcomes, preserved nondeductible IRA basis, NJBEST's $200,000 gross-income boundary, and corrected two-year IRMAA lookbacks. The real Household form has a synthetic January example and visible dated reconciliation output.

Primary authorities checked October 24, 2026: [IRS Publication 550 (2025), Wash Sales](https://www.irs.gov/publications/p550) describes the 30-day before/after window, replacement basis and a December/January example. [IRS Publication 590-A (2025), Nondeductible Contributions](https://www.irs.gov/publications/p590a) permits designation of otherwise deductible contributions as nondeductible. [2025 Form 1040-X instructions, printed page 8](https://www.irs.gov/pub/irs-prior/i1040x--2025.pdf) address changed IRA deductions and Form 8606. [NJ college affordability deductions](https://www.nj.gov/treasury/taxation/individuals/collegededuction.shtml) and [NJ-1040 instructions, lines 37a–c](https://www.nj.gov/treasury/taxation/pdf/current/1040i.pdf) support the implemented NJBEST threshold, with future years remaining explicit frozen-law assumptions. This planning correction is not a filed amended return or a tax-benefit guarantee.

Market-batch household execution, automatic harvesting/sale policies, distributions/fees, retirement replacement lots and broader wrapper adapters remain unfinished.
