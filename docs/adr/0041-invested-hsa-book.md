# 0041. Inside-HSA investments and conditional state basis

Status: accepted, bounded foundation for issue #6. Household withdrawal and market adapters remain separate work.

## Decision

Reuse the existing lot, trade, distribution and fee engine for ordinary HSA securities. The generic taxable-account runner rejects HSA accounts; only the dedicated validated HSA entry point enables them. The Retirement workspace adds **HSA investments**, with editable/importable JSON and downloadable original synthetic results.

Opening positions require independently supplied economic, federal and NJ basis, complete prices and individual HSA ownership. No federal investment tax is generated under the confirmed ordinary-securities/no-UBTI profile. This does not extend IRA wash rules to HSAs. The explicit scope excludes identical outside trading, collectibles, prohibited transactions, UBTI, taxable-account policy engines and unsupported exit-tax comparisons.

NJ taxable-securities/no-wash treatment is an explicitly confirmed assumption. Actual NJ disposal gains use NJ basis; recognized distribution ingredients use their independently supplied NJ character and recognition dates. No state exemption, deduction, historical basis or legal eligibility is inferred. Household annual returns must later combine and limit these ingredients rather than treating gross gains as tax paid.

Only dated observed prices can finance a sale. Opening prices apply until replaced; closing prices become observable on the final date. Cash targets sell permitted liquid lots and retain proceeds inside the HSA. They do not make recipient distributions or create household income. FIFO, federal HIFO and NJ-basis HIFO reuse exact lot disposal. Fixed commissions and cash custodian charges consume actual resources; unpaid fees remain liabilities and take payment priority. Dividend entitlements survive intervening sales, remain receivables until payment and cannot finance early cash requests. Security locks block generated sales and reject conflicting supplied executions.

## Evidence and boundaries

[IRS Publication 969 (2025)](https://www.irs.gov/publications/p969) describes federal tax treatment of earnings retained inside an HSA and distinguishes trustee-withdrawn administration/maintenance fees from recipient distributions. Its prohibited-transaction and pledge rules are outside this ordinary account profile. The [SEC's December 9, 2025 HSA bulletin](https://www.investor.gov/introduction-investing/general-resources/news-alerts/alerts-bulletins/investor-bulletins/health-savings-accounts-hsas-investor-bulletin) describes investment accounts and possible state differences. The locally cached 2024 main-edition [26 USC 223(e)(1)](https://uscode.house.gov/view.xhtml?req=granuleid:USC-prelim-title26-section223&num=0&edition=prelim), dated January 6, 2025, preserves the section 511 UBTI exception; that snapshot is not a verification of all subsequent law. NJ investment treatment remains conditional pending operative state authority and household basis confirmation.

## Runnable checks

The original synthetic example starts with $10,100. Dated share changes produce $1,500 price growth and $100 dividend income, while $5 commissions and $50 custody charges leave $11,645. The $5,000 year-end target is inside-HSA cash, not a withdrawal. Actual conditional NJ ingredients are $100 dividends and $2,490.95 gains, with zero federal investment income. Separate checks cover causal prices, state versus federal selection, unpaid fees, delayed receivables, locks, immutable snapshots, rejected scope and actual UI execution.
