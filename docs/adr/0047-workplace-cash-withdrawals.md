# 0047: Ordinary pre-RMD 401(k) cash withdrawals

Status: accepted. Primary sources checked October 24, 2026 (New York).

## Decision and accounting

Optional `WorkplacePlan.cash_withdrawals` provides dated cash orders and an
explicit source-account profile. This first profile requires a fully vested,
ordinary pretax 401(k), confirmed zero federal/NJ basis, confirmed eligible
nonperiodic distributions, separation date and complete nonduplicated inputs.
It excludes inherited interests, loans, NUA, hardship and other special features.
Designated Roth distributions and direct rollovers require separate profiles.

Actual gross payments are capped by the source balance and outgoing liquidity
locks. First-day orders run before current employee deferrals and month-end
returns; new employee deferrals cannot fund the already separated source plan.
Only net cash enters the shared tax-event ledger. The account loses gross
assets once, and source-withheld federal/NJ tax credits existing annual Payments
once. Withholding is a payment, not additional tax or spendable cash. Federal
withholding is at least 20% for this eligible cash profile; NJ withholding is
an entered scenario rate. Independent cent rounding gives any excess rounding
cent to the federal payment and reduces NJ to the remaining gross amount.

Gross payment is taxable pension in both jurisdictions under the confirmed
zero-basis profile. The existing half-birthday helper determines age 59½.
Earlier distributions incur 10% additional federal tax unless the participant
separated in or after the calendar year they turn 55. Waiting until age 55
after an age-54 separation does not qualify. The exception stays attached to
the workplace source and never changes IRA withdrawal rules. Other early-tax
exceptions require later profiles rather than an inferred exemption.

NJ age-62 pension eligibility uses the distributing owner's year-end age,
not the spouse's age. Existing annual NJ income limits/exclusions decide the
actual taxable return. Existing federal/NJ annual policy assumptions apply;
this feature does not replace frozen future-year tax law with an invented rate.

## Boundaries

The projection rejects this profile if any projected year reaches the source
owner's RMD start age, using the existing RMD-age helper and its explicit 1959
choice only when the horizon reaches a potentially affected age. RMDs are not eligible rollover distributions and cannot silently use
mandatory 20% eligible-distribution withholding. Account-specific RMDs, incoming
IRA rollovers, separate plan basis, Roth plan clocks and employer match/vesting
remain required follow-on retirement work. The retirement ticket stays open.

Withdrawals are supplied fixed requests, not an optimizer or automatic spending
funding policy. Unfilled optional requests remain separately reported; downstream
spending and tax failures continue to reflect actual available cash. No securities
are sold outside the existing marked-value account model, no borrowing is created,
and these synthetic illustrations establish no household entitlement.

## Primary evidence

- [IRS rollover guidance](https://www.irs.gov/retirement-plans/plan-participant-employee/rollovers-of-retirement-plan-and-ira-distributions), eligible distributions and withholding: eligible plan cash is generally subject to 20%; direct rollovers have no withholding; RMDs are excluded from eligible rollover distributions.
- [IRS early-distribution exception table](https://www.irs.gov/retirement-plans/plan-participant-employee/retirement-topics-exceptions-to-tax-on-early-distributions): age 59½ and calendar-year age-55 separation rules; the separation exception applies to qualified plans, not IRAs.
- [NJ GIT-1 & 2, January 2026](https://www.nj.gov/treasury/taxation/pdf/pubs/tgi-ee/git1%262.pdf), printed page 14: ordinary 401(k) contributions on/after January 1, 1984 are generally not included in NJ income when made and distributions are fully taxable; pre-1984 or above-limit contributions require separate recovery calculations. Printed page 9 separately distinguishes direct pretax plan-to-IRA rollovers from later taxable withdrawals. The profile requires confirmed zero NJ basis rather than presuming these facts from an account name.

The local tax-reference collection was searched before current primary-source
verification. The current NJ bulletin qualifies the older archived instructions;
its general contributory-pension rules must not replace its specific 401(k) section.

## UI and checks

Load **synthetic 401(k) cash withdrawals** on Household. Its $100,000 plan pays
$10,000 in February, retaining $90,000. $2,000 source withholding leaves $8,000
for an $8,500 HSA request. Separation in January of the year the owner turns 55
avoids age-based additional tax; the model's $2,000 refund arrives the following
April. Combined wealth stays $100,000. An age-54 separation instead produces
$1,000 additional tax and only a $1,000 refund. The form edits the complete
withdrawal plan and displays gross/net, unfilled amounts, source tax and age flags.

Checks exercise those independent arithmetic cases, exactly/before age 59½,
calendar-year separation, actual liquidity locks, depleted balances, returns on
the remaining plan balance, source-tax rounding, owner-specific NJ age eligibility,
invalid rates/references/dates/provenance, RMD blocking, separated-plan deferrals
and the submitted UI, alongside existing payroll-HSA and tax-cash regressions.
All four realized market methods retain the same gross/net accounting; positive
NJ source withholding reduces optional deposits and credits tax without changing
gross pension income.
