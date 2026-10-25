# 0045. Matched HSA funding policies under employment and market risk

Status: accepted, bounded issues #6/#8 increment. This is a comparison of explicit policies, not the personal optimizer or a calibrated employment probability.

## Decision

Markets / Household funding / **HSA payroll and employment** combines the existing employer-factor/job-loss model with the actual salary-reduction adapter. An observed drawdown can cause next-month job loss, supplied forfeiture and a dated return at reduced pay. Existing retirement cutoffs still stop wages. Actual salary reductions use current wages; they cannot spend later rehire pay or opening wealth as salary. All four existing market methods run the same household ledgers.

The optional automatic personal-cash control is built from the household actually submitted. It copies all non-funding assumptions and requests the same dated HSA amounts as personal deposits, using the same realized batch and path indices. It uses no future path knowledge. Otherwise eligible personal HSA deposits do not require earned wages, so savings can fund them after job loss or retirement. Consequently, matched requests do not guarantee matched funded amounts. The UI displays actual salary reductions, personal deposits, unfilled salary elections, HSA gross assets, tax and wealth for both policies. A supplied alternative JSON and the automatic control cannot silently override each other.

This distinction follows the separate eligibility and salary-reduction treatment in [IRS Publication15-B (2026), Health Savings Accounts](https://www.irs.gov/publications/p15b), alongside the authorities and conditional NJ scope in ADR0044. It does not infer individual employer-plan eligibility or a current state exemption. Cash HSA assets retain declared bank schedules; they are not automatically equity-factor investments. Employer-fund marks and supplied tax allocations retain their existing independent assumptions.

## Tax and cash reporting

Per-path outcomes now separate latest reported recognized tax liability, employee payroll tax, gross actual cash tax payments, dated refunds and net cash tax payments. Original withholding, estimates, settlements and prior-year arrears are counted once. Dated January/terminal wash revisions replace the original annual liability in both the existing Household annual summary and market reporting, without rewriting payment history. Unresolved provisional years and unclosed partial years remain identified. Cash payments concern the projection period; a first annual case can include explicit opening YTD recognition/payments outside that cash period.

Paired results add changes in reported liability and net cash tax payments alongside funding and real wealth. A smaller current cash payment can leave tax owed; a smaller assessment can remain a refund receivable. Neither is an external tax-savings deposit. The same batch/path identity check still applies.

## Independent checks

The original deterministic two-year example has $90,000 wages before retirement. Salary reductions fund $6,000; personal deposits can fund $12,000, continuing from savings after work stops. Employee FICA is $6,426 versus $6,885. With no additional taxable income in the retired year, the extra $6,000 personal deposit changes asset location rather than current tax or total wealth. Salary policy ending nominal wealth is $459 greater under these assumptions.

In the supplied early-crash case, January wages remain $10,000. The next six months have no wages, followed by five months at $5,000. Salary reductions fund $3,000; personal requests fund $12,000 across the two years. FICA is $2,448 versus $2,677.50, but different actual deposits also change the federal deduction. Salary policy ends $70.50 below the personal policy despite its FICA advantage. This is not a claim that either funding route universally wins.

Checks cover all four methods, original input immutability, observed-price job-loss timing, actual contribution/tax differences, January revision/refund timing, partial-year labels, submitted-input control generation, conflicting-policy rejection, and the real Markets form. The two-year example does not cover the age100 safety horizon.
