# ADR 0023: Qualified 529 tuition shares household funding and tax recognition

Status: another integration layer of open retirement #6. Reuses the [529 cash and annual qualification engine](0008-education.md). It does not implement all distribution purposes or complete retirement coverage.

## Actual assets, deposits and bills

A confirmed education plan supplies terms for every household 529, beneficiaries, program cap schedules, opening contribution basis, dated net returns, deposit requests and separate direct-institution tuition bills. Household accounts supply the balances; owners must belong to the filing unit. Deposits use actual available cash after HSA movements and before IRA elections, current tax and spending. The same shared program/beneficiary cap applies across all configured accounts. Unfunded optional deposits remain unfilled requests, not spending failures.

Each tuition request is a confirmed net qualified higher-education bill after aid, credit reservations and other education vehicles. The user must verify institution, enrollment, expense type and applicable room/board limits. These bills must not also appear in ordinary household education budgets; a dedicated confirmation makes that accounting assumption explicit. The initial household profile pays institutions directly. It cannot reimburse owners, pay nonqualified distributions, claim an education credit, or model K-12, credentials, loan repayment, refunds, rollovers or gifts/estates.

The 529 engine applies dated returns, deposits and institution distributions in its existing order. A direct payment reduces wrapper assets once and never enters household cash. At education spending priority, ordinary cash pays only the remaining bill. Any unpaid remainder joins the ordinary education shortfall once. Extra ordinary education budget entries remain additional expenses. Reserve demand includes the actual tuition obligation. Permitted taxable funding quotes the remaining cash bill after wrapper payments, avoiding both duplicate sales and omitted cash needs.

## Basis, qualification and tax

Actual year-end balances and basis carry into the next book. A total investment loss without a funded closing distribution does not erase basis. A zero-value opening account with basis requires explicit confirmation of its unclosed history; generated next-year books retain that confirmation from the preceding actual ledger. A funded full exit records unrecovered basis separately without claiming a deduction. Existing proportional transaction-date basis allocation remains a planning convention requiring reconciliation to actual Forms 1099-Q.

Generated institution payments reserve their own separate net bill once. Actual paid distributions are entirely qualified; the annual engine still reports each account and beneficiary, distributed basis/earnings and no taxable earnings. Unpaid tuition is not a hypothetical distribution. All taxable/nonqualified household distribution adapters remain unfinished.

Actual funded NJBEST contributions enter the annual NJ deduction input once. Manual NJBEST deductions/events are rejected in this profile. The existing annual engine applies its $10,000 return cap and final NJ gross-income threshold, including later funding-sale income. Annual audits recompute the potential deduction using completed gross income. There is no federal contribution deduction or automatic cash refund. Actual income-tax payments remain in the shared tax ledger.

The education engine now accepts published 2025/2026 or an explicit frozen-2026 forward assumption. Actual calendar dates and supplied cap effective dates remain unchanged. This assumption does not convert a program's future cap into verified terms or alter the independently selected federal/NJ tax-policy mode.

## Sources and checks

Checked October 24, 2026: [Publication 970 (2025), chapter 7](https://www.irs.gov/publications/p970) supports qualified-distribution, beneficiary/institution-recipient and benefit-coordination distinctions. The existing local tax-reference collection supplies [2025 NJ-1040 instructions](https://www.nj.gov/treasury/taxation/pdf/current/1040i.pdf); [NJ College Affordability guidance](https://www.nj.gov/treasury/taxation/individuals/collegededuction.shtml), updated March 19, 2026, supplies the current contribution-deduction cap and gross-income threshold. Supplied plan caps remain assumptions, even when a synthetic amount resembles a published program limit.

The two-year synthetic household pays $24,000 tuition, funds $12,000 of 529 deposits, earns $6,960 in the 529 and ends with $24,960 there. Combined HSA/IRA/529 assets reconcile independently to $168,744 after $26,516 tax. Checks cover real form submission, unchanged input round trips, carried basis including total loss, qualified earnings, final-income deduction denial, each confirmation, unknown sources, duplicate deductions, zero-cash shortfalls, sufficient cash fallback and permitted brokerage funding with no duplicate sale.
