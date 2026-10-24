# ADR 0018: Current Medicare premiums collected from household Social Security

Status: another integration layer of open retirement ticket #6. Extends [household Medicare](0017-household-medicare.md) and [household benefits](0012-household-social-security.md); broader wrapper and benefit rules remain unfinished.

The explicitly confirmed `ssa_current_premiums` profile uses one combined monthly payment per recipient. It replaces generated gross benefit cash schedules with dated events containing net cash and gross federally recognized benefits. New Jersey benefit income remains zero. Withheld premiums credit the same healthcare bills; they are neither another cash expense nor a tax deduction. Premium withholding does not generate income-tax withholding. The existing household estimated-payment and settlement system remains available.

## Collection and rounding

Each own, excess-spousal and excess-survivor record retains its separate dollar rounding. For an insured recipient, the own record is the active Part B collection record; a purely auxiliary recipient uses that record. Current Part B is subtracted before lower-dollar rounding of that active benefit and added back to determine gross recognized benefits. Part D IRMAA follows rounding: the entire amount is withheld if the combined remaining payment suffices, otherwise the entire amount stays a cash bill. Ordinary drug-plan premiums and other supplied healthcare costs remain cash-paid.

Coverage in July affects July cash, even when that payment represents June entitlement. A zero receipt before claims start is not a premium deduction. No unpaid premium bill may precede the first positive payment; initial arrears collection requires a separate implementation. Once claims begin without arrears, later cash-only healthcare shortfalls remain supported and visible alongside continuing premium withholding.

The bounded profile excludes premium Part A, hold-harmless/specialized Part B, third-party payers, opening premium credits/arrears and other benefit deductions. Its active Part B record must leave at least $1 after that premium. This is an implementation coverage guard, not a statement of SSA eligibility or its rules for smaller benefits. Combined low-benefit collection, suspension, refund and reinstatement rules are unsupported. The pre-FRA earnings guard and existing all-survive household restrictions still apply; this adapter does not bypass them.

## Reproducible synthetic case

The UI loads a three-year 2030–2032 case with $200,000 opening wealth, $36,000 interest and $144,000 ordinary spending. Both claims begin January 2030 and first pay in February. Published 2026 premium tables are explicitly frozen for this future scenario, independently of frozen income-tax assumptions.

Total gross recognized benefits are $152,243, net cash is $138,040, Part B withheld is $14,203 and total healthcare premiums are $31,888.80. Cash pays $17,685.80 of those premiums. Ending wealth is $212,354.20: opening wealth plus interest plus gross benefits less spending and all premiums. The $7 difference from unadjusted gross-only benefits is record rounding, not a fee. January has no benefit receipt and cash pays $885.80; later months receive $3,944 net and cash pays $480, with $405.80 already withheld. Gross benefits, rather than only net deposits, feed the annual federal benefit calculation.

Checks cover separate record rounding, pure spousal payment, partial-year enrollment, matched higher-IRMAA tiers, insufficient Part D collection, rejected small-benefit profiles, no duplicate cash/tax events, unchanged original inputs and export reproduction. A later spending shock preserves $16,320 unpaid cash healthcare liability while continuing Part B deductions. Tests with independently supplied premium components check arithmetic ordering; those isolated inputs are not asserted to constitute matched published premium tiers.

## Primary sources, checked October 24, 2026

Local QMD discovery produced related Additional Medicare Tax forms rather than supporting benefit-collection passages; those hits were not used as authority. [SSA RS 00601.020](https://secure.ssa.gov/poms.nsf/lnx/0300601020), updated October 21, 2026, supplies separate-record rounding and SMI ordering. [HI 01001.040](https://secure.ssa.gov/apps10/poms.NSF/lnx/0601001040) supplies mandatory collection and coverage/payment-month timing; [HI 01001.041](https://secure.ssa.gov/apps10/poms.NSF/lnx/0601001041) identifies smaller-benefit and arrears rules deliberately excluded here. [HI 00825.110](https://secure.ssa.gov/poms.nsf/lnx/0600825110) identifies the active premium record in dual entitlement.

[HI 03001.001](https://secure.ssa.gov/poms.nsf/lnx/0603001001) establishes full-amount Part D IRMAA collection or CMS billing. [NL 00601.010](https://secure.ssa.gov/poms.nsf/lnx/0900601010) documents combined payments; one combined payment here is an explicit profile assumption. [2025 IRS Publication 915](https://www.irs.gov/publications/p915) includes withheld Medicare premiums in reported benefit amounts. These authorities do not establish personal enrollment, future premium amounts or benefit eligibility.
