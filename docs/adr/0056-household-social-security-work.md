# 0056: Employment work tests share household cash, tax and government positions

Status: accepted bounded household adapter for open retirement issue #6.
Depends on [own-record work-test accounting](0055-social-security-work-test.md).

Household adds an editable optional `social_work_plan` and a synthetic earned-wage
example. Its claim case and projection must cover the same complete calendar
years. Actual work wages remain null in the submitted policy: the adapter derives
them from actual current earned-USD W2 income streams after employment-path
preparation and before employee401k/HSA reductions. Reported January wage forecasts
remain separate supplied inputs. Existing tax validation enforces wage recipient
mapping. Manual/opening W2 and employer-compensation allocations require earned-
month classification and block this profile; foreign work, self-employment and
special wage payments remain excluded by the work policy's explicit confirmations.

The generated net benefit source enters actual household cash and federal Social
Security recognition once. It is excluded from NJ income and payroll wages. The
ordinary source is replaced, rather than added alongside a second check. Dated
refunds and ARF arrears enter receipt-year benefits; current recoveries reduce
those same net benefit receipts. The supported collection method only recovers
from available positive benefits, so this profile creates no negative annual
benefit input or automatic credit for repayments exceeding benefits. Medicare
SSA withholding is blocked; supported direct-billed premium cash can coexist.

Government refund/ARF claims are separate from wallet balances and liquid
reserves. Recognized claims add to net wealth at face value; overpayment debt
reduces it. Their conditional settlement dates still determine spending cash.
The existing nominal/real household wealth and funding-shortfall calculations
therefore retain unfunded spending when an unpaid claim cannot pay a bill.
The UI shows monthly positions and completed annual earned-wage assessments.
Source exports preserve claims, forecast policy and gross payroll instead of
serializing generated benefits as another independent original income source.

Meaningful synthetic checks include the original$491 partial-check refund, later
$300 ARF arrears, explicit government debt, a retirement-date change producing
a later$3,372 reconciliation, and a zero-cash household whose$3,372 claim cannot
pay January's$238 spending gap. Current$30,242 earned W2 and$2,810 net SSA cash
produce$1,405 taxable SSA under the frozen tax case. A funded$1,000 pretax401k
deferral reduces federal AGI to$30,647 but preserves the work test's gross wages
and$491 reconciliation. Adding an unexpected December wage leaves all eleven
earlier complete household rows identical, then creates carried debt and later
recovery. Existing no-work, spouse/survivor, Medicare and household-benefit checks
remain part of affected regression coverage.

Tax treatment uses the existing explicit annual rule mode and **no special
lump-sum election**, as confirmed in the work policy. It is not a reconstruction
of a prior-year return or automatic election advice. Initial QMD vector discovery
found the2025 Form1040 instructions' Social Security/repayment discussion; their
lines6a/6b section was read. The more specific current primary publication was
then verified online: [IRS Publication915 (2025)](https://www.irs.gov/publications/p915),
**How To Report Your Benefits**, **Lump-Sum Election**, and **Repayments More Than
Gross Benefits**. Net SSA1099 box5 amounts govern ordinary reporting; retroactive
payments ordinarily enter the receipt year, with a distinct optional election.
These published2025 rules support the existing frozen-rule tax profile; they do
not establish later legislation, cross-border eligibility or an optimal election.

Own-record/all-survive restrictions, complete wage history, first grace-year
rules, fixed supplied PIAs, frozen2026 work limits, collection assumptions and
ARF processing remain those of ADR0055. Dated-death household filing/account
transitions, auxiliary work effects, special histories, earnings-to-PIA
recomputation, SSA Medicare collection and special tax elections need separate
supported adapters. This synthetic projection does not establish lifetime
spending safety or complete retirement-ticket delivery.
