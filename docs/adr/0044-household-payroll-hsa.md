# 0044. Qualifying HSA salary reductions in actual payroll

Status: accepted, bounded issue #6 increment. Employer excess corrections and remaining workplace distribution/rollover/match rules are separate work.

## Decision and authorities

An optional `hsa_plan.payroll` declares qualifying section125 W2 employees, complete elections, gross wages before salary reduction and no unknown other payroll reductions. Ordinary after-tax payroll deductions remain personal deposits. Partners and ineligible S-corporation owners are outside this confirmed profile.

The [2026 IRS Publication 15 HSA section](https://www.irs.gov/publications/p15) distinguishes ordinary payroll deductions from qualifying section125 salary reductions and their federal wage/employment-tax treatment. [2026 Publication 15-B](https://www.irs.gov/publications/p15b) describes monthly HSA eligibility, contribution limits, employer reasonable belief, and partner/S-corporation restrictions. The [2025 Form8889 instructions, line2](https://www.irs.gov/instructions/i8889) classify salary reductions as employer contributions rather than personal deductions; the installed local 2025 reference, page4, supports the same distinction. These authorities do not establish individual eligibility or NJ conformity. The existing NJ profile remains an explicitly supplied taxable-wages assumption.

## Funding and accounting

First-day monthly orders use the owner's actual pooled current-month gross USD wages after all funded employee401k elections, including Roth. One owner cannot borrow a spouse's pay, future earnings or opening wealth to create salary-reduction room. The shared HSA book supplies actual remaining annual eligibility capacity and actual cash. Unfilled optional requests remain visible without becoming medical spending failures. Required excess employer funding still requires an explicit correction adapter.

Actual salary reductions move gross payroll cash into the same HSA once. They are employer-reported contributions but do not create external employer wealth or a second personal deduction. Reuse the existing wage-stream reduction function without emitting pension-deferral addback: federal income and payroll wages both decline. Existing pretax401k deferrals still retain their payroll treatment. Under conditional NJ treatment, the zero-cash HSA event restores the salary amount to NJ wages. Actual withholding and taxable-sale funding trials use that same independent NJ wage base, so a federal exclusion cannot silently reduce state withholding or underfund it.

Payroll precedes other HSA events, optional post-receipt deposits and current tax/spending, following the existing monthly employee-payroll convention. It is not an intramonth pay-date certification. First-day investment events precede payroll deposits; contributed cash enters the persistent investment book and settles custodian arrears. The eligibility book's monthly opening captures payroll counters and orders for one later tax/audit recognition, while annual resets carry actual account values and shared receipts. No external deposit is manufactured for a tax saving.

## UI and checks

**Load synthetic payroll HSA household** uses the real Household editor with $120,000 wages, employee401k elections, $6,000 salary reductions, a $1,000 personal HSA deposit, $500 external employer funding and a historical qualified reimbursement. Actual HSA cash ends at $7,000. Federal AGI is $89,000, employee payroll tax $8,721 and conditional NJ gross income $96,500. Employer-reported HSA contributions are $6,500, of which only $500 is external funding. All household capital reconciles to opening assets plus gross wages/external funding less actual tax.

The matched personal-deposit case has the same AGI and NJ liability/withholding, but $9,180 employee payroll tax; the $459 wealth difference equals 7.65% of $6,000 in this below-wage-cap example. Other checks cover coupled Roth/pretax401k room, absent owner wages despite savings/spouse pay, annual HSA limits, job loss, eligibility/input guards, year-boundary receipts and room, invested cash/fees, actual withholding versus funding trials, and the real UI.
