# 0048: Required workplace withdrawals by complete plan

Status: accepted. Source checks: October 24, 2026 (New York).

## Problem and decision

A qualified plan must satisfy its own RMD; an excess payment from another plan
cannot cure the shortfall. Separate investment subaccounts within one plan must
share that plan's target. Optional `cash_withdrawals.rmd` supplies complete plan
groups, beneficiary-table eligibility, frozen-2026 rule assumptions, an explicit
December31 deadline and a source-withholding policy. All classified pretax workplace
accounts appear in exactly one group, with one owner, one separation history and consistent birth-1959
start-age assumptions. No unmodeled opening shortfalls may be omitted.

The existing pinned Owl/IRS divisor helper determines the target from each
plan's actual prior-December balance. The target is rounded upward to cents and
fixed before January withdrawals, deferrals or returns. Later gains/deposits do
not increase it; next January uses actual closing balances. Uniform versus sole
spouse more than ten years younger is explicitly confirmed, with the actual
household spouse's birth date required for the joint table. Source owner, plan
identity and beneficiary eligibility are never inferred from an account name.

Actual gross cash payments consume that plan's remaining requirement first.
The RMD portion uses the separately supplied noneligible federal withholding
rate (default10% for this confirmed nonperiodic cash profile); eligible remainder
retains at least20%. NJ withholding remains an entered rate. Combined rates and
cent rounding cannot produce negative recipient cash. Existing source-payment
credits, net wallet receipts and delayed refunds are reused without another cash
draw or tax-saving deposit.

When enabled, December1 catch-up follows manual first-day orders and uses each
group's sources in listed order. It uses only actual unlocked balances; later
month-end returns cannot fund the earlier payment. No catch-up occurs for a
satisfied or zero-balance plan. Employee deferrals remain excluded from an already
separated source, and their annual wage/limit accounting is unchanged.

## Shortfalls and contingent tax outcomes

Unpaid requirements fail the household funding assessment in December. They are
internal asset-transfer obligations, not another spending expense subtracted
from wealth. Ordinary25% shortfall excise enters the existing federal additional
retirement-tax field with zero cash/income recognition. Conditional10% timely
correction or allowed IRS waiver cases require explicit confirmation and remain
labeled assumptions. The model does not infer a filing, actual correction or IRS
decision. Excise is calculated on the filing unit's aggregate shortfall at the
selected rate; cumulative allocation of cents keeps per-plan audits equal to
the total. Income-tax withholding is credited against actual liability normally.

A missed prior-year requirement remains unresolved and continues to fail funding;
changing years, paying excise or satisfying the next target does not silently
cure it. Later corrective cash and prior-return excise revisions still require
an adapter. The enum's contingent relief cases do not establish eligibility or
create cash for an unmodeled future correction. This limitation stays visible
beside results; the retirement ticket remains open.

## Source evidence and remaining scope

- [IRS RMD FAQs](https://www.irs.gov/retirement-plans/retirement-plan-and-ira-required-minimum-distributions-faqs), Q4/Q5: prior-December value and applicable table; qualified plans separately, in contrast to permitted IRA/403(b) aggregation. Q8/Q9/Q10/Q12 cover conditional shortfall tax, waiver, no future excess credit and RMD rollover exclusion.
- [2026 Form W-4R](https://www.irs.gov/pub/irs-pdf/fw4r.pdf), page2: nonperiodic default10% with permitted elections, versus eligible rollover distributions' minimum20%. Periodic payments use a separate withholding profile, not an inferred W-4R election.
- [2025 Form 5329 instructions](https://www.irs.gov/instructions/i5329), PartIX: shortfall tax belongs to the year including the distribution deadline; reduced tax requires actual correction and a return within the correction window; waiver requires an IRS decision.
- [2024 final RMD regulations](https://www.govinfo.gov/content/pkg/FR-2024-07-19/html/2024-14542.htm) and [separate proposed rules](https://www.govinfo.gov/content/pkg/FR-2024-07-19/html/2024-14543.htm) distinguish operative provisions from proposed corrective-distribution ordering. This layer does not implement the proposal as established current law.

The local tax-reference collection was searched before primary-source checks;
its unrelated ranking hits were not used as evidence. Existing zero federal/NJ
basis and ordinary vested source confirmations still apply. Current-employer
RMD deferral, pre-separation access, first-April deferral, opening/later corrections,
nonzero plan basis, Roth plan distributions, inherited/special interests and
rollovers remain required follow-on work. Each source must be separated by
December1 in every RMD year supported by this cash profile.

## Synthetic example and executed checks

Household loads **synthetic separate-plan RMDs**. Alpha has two $123,000
subaccounts and beta a $246,000 balance. At age75, each plan's divisor24.6
requires $10,000. Alpha pays $15,000 in February: $10,000 RMD plus $5,000 eligible
remainder produce $2,000 withholding and $13,000 net cash. Beta independently
pays $10,000 in December, withholding $1,000. With this illustration's zero final
liability, the $3,000 refund arrives next April. Wealth remains $492,000.

The next targets use actual closing assets: alpha$231,000/23.7→$9,746.84;
beta$236,000/23.7→$9,957.81. Locking beta through December instead leaves its
$10,000 shortfall, default$2,500 excise and $500 additional household tax payment
after alpha's $2,000 credit. Unresolved beta remains visible in January.

Checks cover those independent arithmetic cases, group identity, beneficiary
eligibility, source rates, prior-December snapshots, changing years, gains,
zero balances, automatic-only schedules, actual locks, contingent excise cases,
aggregate cent allocation, submitted Household forms and existing withdrawal
regressions. The UI exposes targets, actual payments, shortfalls, excise cases
and underlying prior-December balances.
