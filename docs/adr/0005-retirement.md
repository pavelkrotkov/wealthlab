# ADR 0005: Retirement funding

Status: original contribution-layer design under #6. For the current combined feature, see [retirement coverage and limits](../retirement-coverage.md); this ADR records the narrower initial workbench.

The Retirement workspace begins with an annual, dated contribution allocation. It accepts published 2025/2026 cases and [explicit frozen-2026 forward assumptions](0016-future-contribution-assumptions.md). Each owner supplies eligible compensation, separate traditional/Roth IRA MAGI, workplace coverage, plan permission and prior-year wages from the sponsoring employer. These are forecasts requiring confirmation. All current-year contributions must be orders; opening balances represent prior-year history. Existing excess contributions and their correction are outside this layer.

IRA capacity is shared across the owner's traditional/Roth destinations. Joint filers explicitly reserve compensation budgets whose sum cannot exceed combined eligible compensation. This conservative policy permits spousal funding without silently reallocating unused budgets after future funding failures. Workplace traditional/Roth employee deferrals share a cap. Only one covered employer per owner is modeled; employer contributions, multiple-sponsor catch-up allocation, 403(b), 457, SIMPLE and SEP exceptions need further models.

Receipts precede orders on the same date. Orders retain their supplied priority within a date. Each reports requested, permitted, funded, blocked-by-limit and unfunded amounts. Only funded amounts consume limits and enter the destination. Earlier failed requests are not automatically retried when later cash arrives. Opening assets plus receipts always equal ending cash plus assets. Separate account IDs preserve the difference between IRAs and workplace plans even when both have a traditional wrapper.

Federal IRA deductibility uses actual funded amounts and owner-specific coverage/MAGI. Nondeductible contributions become federal basis; NJ contributions produce separate previously taxed basis. Roth regular contributions remain distinct from designated Roth workplace money. Payroll and tax liabilities are not calculated here; a pretax wage exclusion is not a payroll-tax exemption. This workbench remains contribution allocation. The [household employee 401(k) bridge](0019-household-employee-deferrals.md) now applies current-payroll funding and annual tax recognition; ordinary IRA contributions and complete wrapper withdrawal basis remain unfinished.

## Rule provenance

Verified October 23, 2026. [IRS Publication 590-A (2025)](https://www.irs.gov/publications/p590a) supplies shared IRA/compensation limits, spouse and coverage distinctions, deduction phaseouts and Roth worksheet ordering. The implementation retains decimal precision before rounding reduced limits upward to $10, with the worksheet minimum where applicable; compensation still caps permission. [Notice 2025-67](https://www.irs.gov/pub/irs-drop/n-25-67.pdf) supplies 2026 dollar limits and phaseout updates. [IRS catch-up guidance](https://www.irs.gov/retirement-plans/plan-participant-employee/retirement-topics-catch-up-contributions) establishes age-based limits and the prior-sponsor-wage Roth requirement beginning in 2026. [NJ deduction guidance](https://www.nj.gov/treasury/taxation/njit13.shtml) disallows the traditional IRA deduction; its [retirement guidance](https://www.nj.gov/treasury/taxation/njit6.shtml) distinguishes previously taxed contributions. No future year's law is inferred.

## Original delivery map for #6

1. Traditional/IRA/Roth withdrawals, annual pro-rata recovery, independent NJ basis, conversion clocks, early access and RMDs; source balances must fund distributions exactly once.
2. HSA and education eligibility, contributions and qualified/nonqualified distributions.
3. Dated Social Security, spouse/survivor cases, work/benefit interaction, Medicare and IRMAA history. Reuse supported Owl calculations with an explicit scenario year.
4. Household ledger and tax integration, lockable schedules, actual shortfalls and matched Owl comparisons. IRA annual reconciliation cannot give earlier policies knowledge of later market returns.

The [October 25 coverage audit](../retirement-coverage.md) maps the five ticket acceptance criteria to implemented workbenches, household adapters and checks. It supersedes historical remaining-work statements in this ADR; unsupported combinations stay explicit and do not silently enter household projections.
