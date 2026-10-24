# ADR 0021: Actual household cash funds IRA deposits and carried basis

Status: household contribution integration under open retirement ticket #6. Extends [fixed household IRA schedules](0015-household-ira.md) and the [combined annual IRA engine](0020-current-year-ira-deposits.md). HSA/education funding, special benefit worksheets and other documented rule gaps remain unfinished.

An optional IRA contribution plan supplies each year's rule mode, eligibility/MAGI forecasts, owner compensation budgets and all dated IRA requests. The household supplies the opening account book and actual cash; input forecasts cannot create another balance or receipt. The existing complete-calendar-year, ordinary-IRA, owner/birth, no-duplicate-tax and year-end settlement guards still apply. Workplace accounts remain outside IRA pools. Unknown or incomplete annual eligibility blocks calculation.

## Cash priority and monthly settlement

Household income, refunds and dated receipts, including IRA withdrawal cash, arrive before optional IRA deposits. Existing prior-tax arrears are paid first. Deposits then use available wallet cash before current withholding/settlement and ordinary spending. This priority is explicit: a large elective deposit may leave a spending or tax shortfall. Permitted taxable sales remain available under their existing rules; no new borrowing or automatic IRA withdrawal is inferred.

Requests settle at month end after that month's IRA returns and withdrawals/conversions. This is a monthly pooled-cash convention, not an intramonth payroll or banking forecast. Only actual funded amounts enter the combined IRA engine, paired with equal internal funding receipts. Those internal receipts are bookkeeping transfers and are not household income. The engine's withdrawal cash is credited through the existing household tax-event path once. Earlier failed deposit or withdrawal requests are not retried after later money arrives.

The existing annual engine recomputes only the current year's fixed schedule when its funded deposit book changes. The cache is confined to one projection with fixed schedules and append-only actual deposits. Zero-funded requests remain in the original audit without creating funding events. Applied balances come from current-month events; later modeled values never enter an earlier wallet. Final December reconciliation supplies taxable IRA amounts, early-distribution tax and the maximum funded deduction. Federal/NJ basis, Roth regular contributions, first Roth year and conversion buckets carry into the following year's actual book. In-year figures still omit unfinalized IRA tax and deduction effects.

## Completed eligibility and accounting checks

The shared completed-tax check runs after tax funding and settlement. A sale used to fund taxes can realize a gain that changes Roth eligibility. Neither cash availability nor a stale low-MAGI forecast can prove that a funded deposit qualifies. W-2 compensation, the actual maximum deduction and actual funded Roth eligibility are checked using completed scenario income. Unsupported Social Security deduction worksheets, AGI-dependent passive-loss refiguring and other compensation adapters block this combined profile, as in ADR 0020.

Manual IRA income, additional tax and deduction inputs cannot duplicate the generated events. A small receipt hook in the tax ledger recognizes only its returned events; it does not replay original plan events. Unfilled optional deposits are displayed separately from spending failures and do not add basis. Ordinary cash shortages and unpaid taxes remain failures, with remaining IRA assets unable to hide them.

## Reproducible synthetic case

The two-year household begins with $10,000 cash, $100,000 traditional IRA and no Roth balance. It earns $120,000 W-2 wages, spends $48,000 and funds $12,000 IRA deposits. Fixed traditional withdrawals total $40,000, a $10,000 conversion stays invested and a later $5,000 Roth withdrawal consumes regular contribution basis. Under the separate frozen tax/rule assumptions, annual federal AGI is $87,000/$77,000. Maximum IRA deductions are $3,000 each year; the early traditional withdrawals also incur the modeled ten-percent additional tax.

Total federal/NJ/payroll/additional tax is $27,914. Ending cash is $87,086, traditional IRA $56,000 and Roth $11,000: wealth $154,086 equals $110,000 opening wealth plus $120,000 wages less $48,000 spending and $27,914 taxes. Transfers and conversions cancel. Ending NJ traditional basis is $3,777.21; federal traditional basis is zero, Roth regular basis $1,000 and the $10,000 taxable conversion bucket remains intact.

Checks cover this reconciliation, nondeductible basis, actual withdrawal receipts funding a deposit, no later backfilling, no plan-event replay, original-input immutability and JSON reproduction. An empty deposit policy matches the existing fixed IRA profile including dated returns. Paired equal-liquidity taxable accounts distinguish full basis from a gain: the no-gain case supports the deposit, while the tax-funding gain makes its funded Roth deposit ineligible and blocks the projection. The real household editor exposes funded/unfilled deposits and completed eligibility alongside cash and tax results.

Primary tax authorities and their dated scope remain those in ADR 0020. These examples establish accounting behavior under stated assumptions, not personal eligibility, actual household facts or retirement safety.
