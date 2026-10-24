# ADR 0022: Household cash HSA funding and historical reimbursements

Status: a household integration layer of open retirement ticket #6. Reuses the [HSA cash book](0007-hsa.md), monthly eligibility limits and global receipt accounting. This profile does not complete HSA or education coverage.

## One household cash book

The optional HSA plan supplies complete annual eligibility contexts, dated personal deposits, direct employer funding, bank interest and qualified-only reimbursements. Existing USD cash HSA accounts supply opening balances. All household members and births must match; establishment history must remain consistent. A spouse without an HSA can supply coverage with an unset establishment date; every actual account holder needs a known date. Enabled household Medicare coverage must agree with monthly HSA eligibility flags.

After ordinary receipts and prior-tax arrears, HSA requests run before IRA deposits, current taxes and ordinary spending. The existing HSA engine preserves dated order within each month; household ordinary income remains a monthly receipt convention. Failed personal requests are not retried and create no deduction. Direct employer funding is external compensation, not a withdrawal from household cash. Excess employer requests block this profile: silently discarding employer compensation would be incorrect, and payroll/correction treatment is unfinished.

The HSA account balances update the household wallet once. Reimbursements transfer existing capital into cash; personal deposits transfer cash into the HSA. Neither changes wealth. Employer funding and bank interest add assets once. Zero-cash recognition events feed actual funded personal deductions into federal Tax-Calculator input `e03290`; they cannot deposit the transfer a second time. Out-of-pocket personal contributions preserve gross payroll wages and FICA. Salary-reduction contributions need another adapter.

Each new calendar year resets contribution room using that year's explicit rule mode and actual carried account balances. The remaining medical-receipt ledger carries across years and all accounts. Annual audits retain rule/base year, limits, actual deductions, employer amounts, bank interest and remaining receipts. Only published years or explicitly frozen-2026 assumptions are accepted by the existing rules layer.

## Historical receipts and conditional state treatment

Receipts must already have been paid before the projection begins, after the withdrawing owner's HSA establishment. Their earlier payment belongs in opening household history. Prior federal deductions and other reimbursements remove qualified capacity; one shared ledger prevents reuse across years or spouses. Qualified-only withdrawals stop at available HSA cash and remaining eligible receipts. New medical bills, direct payments, nonqualified household withdrawals and ordinary-income/additional-tax recognition remain unfinished. The standalone HSA workbench still exposes nonqualified-distribution ingredients separately.

The user must explicitly confirm the conditional NJ bank assumption: no personal deduction, employer contributions added to NJ wages, current taxable bank interest. The same employer amounts must be excluded from other NJ wage inputs. This is a scenario assumption, not a verified NJ legal conclusion; results, controls and audits display that distinction. Securities, state lot basis, fees, special interest exemptions, rollovers, excess corrections and last-month/testing-period rules are unsupported here.

## Evidence and verification

Checked October 24, 2026: [2025 Form 8889 instructions](https://www.irs.gov/pub/irs-prior/i8889--2025.pdf) and [Publication 969](https://www.irs.gov/publications/p969) support funded personal deductions, annual eligibility and qualified-distribution restrictions. The existing local tax-reference collection supplied the 2025 instructions; no earlier-year dollar limits were substituted. [Notice 2004-50, Q&A 38–39](https://www.irs.gov/irb/2004-33_IRB) supports shared-expense nonduplication and delayed reimbursement with retained evidence of eligibility, no other reimbursement and no prior itemized deduction. Those federal sources do not establish the selected NJ treatment.

The synthetic two-year household starts with $10,000 in its HSA. Personal deposits of $8,000, employer funding of $2,000 and $300 interest, less $3,000 historical reimbursements, leave $17,300. A further $1,000 reimbursement request remains unfilled. Total household wealth reconciles independently to opening assets plus wages, employer funding and interest, less spending and actual tax liability. Checks cover unchanged payroll tax, IRA MAGI interactions, prior deductions, cash shortfalls, year-to-year receipt reuse, missing/conflicting establishment dates, duplicate tax inputs, excess employer funding, Medicare consistency, immutable round trips and real form submission.
