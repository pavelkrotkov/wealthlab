# ADR 0033: Long/short economics on paired market paths

Status: first product-model layer for open ticket #9. The economic engine and UI are implemented; conditional private-fund taxes, basis/exit recognition and household integration remain required. No new dependency.

## Balance sheet and monthly convention

Opening long/short notionals are supplied multiples of investor equity. Short proceeds are segregated collateral: they earn no interest, cannot finance longs and are not income. Long purchases use equity and then a full-recourse loan. Free cash and the loan remain separate. Net equity is long value plus free cash and collateral, less the short liability and financing loan. Outside cash is a separate zero-return reserve, and investor wealth includes it exactly once.

Entry turnover costs reduce equity. An opening maintenance check can use actual outside cash before any return. Monthly marks change both legs; separate long cash yield enters free cash/loan repayment, while the short's cash yield is an economic substitute-payment cost. Borrow fees, financing and manager fees use opening short notional, loan and positive equity, respectively, at the supplied annual rate divided by twelve. Loan interest continues on unpaid debt after liquidation. Deductibility is not inferred.

After marks and costs, a supplied maintenance fraction of gross exposure can require collateral. A confirmed policy either liquidates or first uses finite outside cash. Insufficient funding remains a failure. Locks prevent a complete unwind and retain assets and liabilities. Liquidation can consume remaining outside cash and leave a full-recourse debt; losses are never capped at the opening investment.

Month-end redemption requests scale both legs and collateral, pay actual net proceeds and retain unfilled requests. Optional monthly/quarterly/annual rebalancing targets observed pre-trade equity, charges actual turnover and rechecks margin. Reported post-cost leverage can therefore differ from target multiples. A terminal exit respects locks. This monthly convention does not certify intramonth broker compliance, settlement, availability of borrow or daily prices. Complete write-off factors require a separate delisting/reinvestment adapter and are rejected.

## Paired UI and boundaries

Products / Long/short economics edits a sleeve, a separate unlevered reference and market assumptions. Both start with identical investor capital/outside cash and use one realized batch. The reference has no shorts, at most 100% long exposure and a supplied 100% gross-maintenance rule: fee-induced deficits must use actual reserve cash or unwind, rather than quietly borrowing. Reference fees are independently editable. Deterministic, correlated Monte Carlo, supplied historical replay and named stresses include an additional short squeeze. The default history is explicitly invented.

Outputs show exposures, collateral, loans, cash, costs, redemptions, forced/blocked exits and paired **pre-tax** wealth. Source terms and realized observations are exportable. Margin failure is not yet a household spending outcome. This layer has no inferred tax-loss generation, legal tax classification, basis ledger, private-fund contract, after-tax ranking or household allocation adapter. Those remain required under #9.

## Checks and authorities

Independent cases reconcile a flat $100,000 130/30 sleeve plus $10,000 outside cash to $110,000 after unwind; borrowing, financing, manager and dividend costs to $109,400; and actual entry/rebalance costs to $109,682.20 in a price-change case. A 400% short-price increase creates a $120,000 economic loss and leaves $10,000 unpaid debt after using the $10,000 reserve. Other checks cover funded calls, locked insolvency, redemptions, unchanged inputs/shared paths, all four modes, scope guards and actual form submission.

Checked October 24, 2026: [SEC investor margin bulletin](https://www.investor.gov/introduction-investing/general-resources/news-alerts/alerts-bulletins/investor-bulletins-29) supports retaining losses beyond capital and possible forced sales. It does not validate the supplied gross-maintenance formula. [IRS Publication 550 (2025), Short Sales and Wash Sales](https://www.irs.gov/publications/p550) distinguishes closing a short, holding-period rules, loss restrictions and substitute-payment treatment. Consequently economic P&L is not automatically a deductible ordinary/capital allocation. The local tax-reference search also located an older 2024 edition; that was not substituted for current 2025 primary evidence.
