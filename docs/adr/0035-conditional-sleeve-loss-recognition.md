# ADR 0035: Conditional supplied loss recognition

Status: another part of open #9. Reuses the actual household tax ledger; private-fund contracts, basis/exit recognition and general business-loss eligibility remain unfinished. No new dependency.

## Separate income from eligibility assumptions

Each supplied sleeve allocation has independent federal and New Jersey loss timing. Positive components stay on the original allocation date in every case. Negative components are either denied, allowed on the original date, or deferred until an explicit later assumed release date. Denial cannot discard associated positive income. Deferral moves only negative items and never creates a cash receipt. Dates after the projection remain unrecognized inside that projection and remain visible in the exported source/audit.

Allowed or released negative amounts require an explicit eligibility-after-limits assumption. This means eligibility as an annual-return input, not an inferred legal conclusion or automatic permission to offset wages. Existing federal capital-loss/carry and NJ category/business rules still run in the authoritative annual engine. Federal capital character and already-allowed passive ordinary character remain distinct. A generic trading/business ordinary loss is not silently mapped into passive income. NJ dispositions and NJ partnership income have independent character and loss assumptions. Unsupported tax fields and manual dated carries remain rejected.

This is a conditional recognition adapter, not a basis or suspended-loss calculation. It does not decide basis, at-risk, passive-activity, excess-business-loss or investment-interest eligibility, nor infer the effect of a denied deduction on basis. Those determinations and complete exit assumptions need separate validated inputs/models before a fully liquidated after-tax ranking. The source negative amount is a supplied schedule, independent of the economic book's P&L. The synthetic example is an illustration, not a provider forecast or generated tax alpha.

## UI, cash and checks

Markets / Household funding / Long-short household offers independent denied/deferred/allowed synthetic controls. The editable and exportable JSON includes each allocation's amounts, character, timing and assumption confirmation. The result exposes original negative amounts and complete recognition schedules beside the basis limitation. Household JSON imports use the same validator and computation. Every recognition event has zero cash; actual annual liability/payment timing determines cash retained or paid.

Checks preserve positive income in denied cases, defer only federal losses while independently allowing NJ losses, reject inconsistent dates/unconfirmed eligibility, and run all three cases through an actual household return. A $50,000 short-term gain with a separately supplied $12,000 long-term loss yields federal AGI $38,000 only in the allowed case; denied or beyond-horizon deferred loss leaves $50,000. A separate negative NJ partnership category does not reduce the positive disposition category. Household ending wealth reconciles to opening capital less actual tax, with no hypothetical tax-saving deposit.

## Evidence checked October 24, 2026

The local tax-reference collection supplied the 2025 partner K-1 instructions pp. 6–7 and Publication 925 p. 11; older provider editions were not substituted. [IRS 2025 K-1 instructions](https://www.irs.gov/instructions/i1065sk1) separate basis adjustments and allowable/suspended loss items. [IRS Publication 925 (2025)](https://www.irs.gov/publications/p925) distinguishes portfolio losses from passive deductions and applies basis/at-risk limitations before passive limits. [New Jersey business-income guidance](https://www.nj.gov/treasury/taxation/njit11.shtml) keeps partnership income in its own category and does not enter an aggregate negative partnership amount against unrelated income. These sources motivate the scope boundary; they do not establish eligibility for any named product.
