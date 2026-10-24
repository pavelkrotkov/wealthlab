# 0042. Actual invested-HSA household funding

Status: accepted; another bounded issue #6 increment. Payroll/cafeteria HSA funding, automatic medical deductions and investment market compilation remain unfinished.

## Decision

An optional `hsa_plan.investments` uses the invested-HSA book from ADR 0041. Account IDs, individual owners, USD currency, zero generic account fees, opening marked value and the entire inclusive/exclusive household horizon must agree. Clear the all-cash declaration and explicitly confirm that remaining HSAs are cash accounts and generated NJ investment income is excluded from other inputs. Known identical outside taxable securities are rejected; no IRA wash classification is inferred for an HSA.

One persistent investment book supplies the annual eligibility/medical book's actual cash balances. The monthly wallet instead carries marked securities, cash and unpaid dividend receivables. Investment fee arrears remain a separate liability, deducted exactly once. The annual eligibility reset carries actual cash, persistent positions, separate state basis, fee obligations and shared receipt history; it never reopens shares at a new basis.

Personal deposits, actual employer funding and bank interest enter their original HSA cash account once. Cash arriving while custodian fees remain owed pays those arrears. Recipient withdrawal eligibility is determined before requesting liquidation. Permitted liquid shares can then be sold at the latest observed quote, using the selected FIFO/HIFO/NJ-HIFO rule and actual commissions. Unfunded requests cannot spend marked positions or unpaid dividend receivables.

Investment observations and entered trades on a date precede recipient orders on that date. Recipient orders retain their actual chronology; the explicit month-end medical retry can observe later deposits and locks. An unpaid provider bill temporarily supplies eligibility for its current direct payment. After that attempt, restore only previously paid, undeducted household-cash receipt capacity. Neither an unfilled election nor a temporary eligibility seed becomes a historical receipt. Only actual provider payments discharge the bill; household cash fallback and remaining liability keep the existing medical accounting.

Actual realized NJ lot gains and independently declared distribution character enter the household return as zero-cash income events. Federal investment income stays inside the HSA in the confirmed ordinary/no-UBTI profile. Under the conditional NJ taxable-securities profile, linked recipient taxable fractions must be zero to avoid retaxing already recognized investment income/principal. Cash-only accounts keep their separately declared fractions. Actual nonqualified recipient distributions still use the independently selected federal ordinary-noninvestment assumption and existing age/disability additional-tax rules. These are conditional profiles, not conclusions about historical NJ basis or eligibility.

## Checks and UI

**Load synthetic invested HSA household** executes the real Household editor. Opening cash plus HSA assets are $11,100. A $5,000 direct provider payment requires an actual sale at the observed $120 price; $1,000 household cash pays the rest. The entitled $100 dividend, $2 commission, $50 custodian fee and actual marked remaining shares reconcile to $6,548.17 net wealth. NJ ingredients are $2,399 realized gains and $100 dividends; federal investment income is zero. The $50 fee remains owed because the provider consumed all available HSA cash, and is deducted once from gross assets.

Checks cover ineligible claims without sales, locked investments leaving bills owed without phantom receipts, actual annual NJ liability, nonqualified distribution taxes, year-boundary position/basis continuity, later deposit payment of fee arrears, opening-value and scope guards, existing cash-HSA regressions and the actual UI. Downloads include the final investment audit beside medical and annual eligibility records.
