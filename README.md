# Wealthlab

A local-first financial scenario workbench with editable household cash flows, federal/NJ tax assumptions, actual tax lots, retirement wrappers and benefits, employment paths, matched markets and conditional investment-product models. See [retirement coverage and limits](docs/retirement-coverage.md) for supported profiles. Additional products, cross-border scenarios, optimization and release integration are still being built; the implementation plan tracks the remaining work.

The intended workflow is to define a household, compare explicit policies under the same market paths, inspect spending shortfalls and taxes, and explore better policies within user-set bounds.

- [Scope and glossary](CONTEXT.md)
- [Software reuse research](docs/software-research.md)
- [Implementation tickets, dependencies and acceptance checks](docs/implementation-plan.md)
- [Architecture decisions](docs/adr/0001-local-scenario-workbench.md)

The public repository contains code, public-source references and synthetic fixtures only. Household records, account exports, credentials and private illustrations stay outside version control. No brokerage trading or account connection is planned for the first complete version.

## Delivery standard

Every feature must work through the UI and calculation engine, expose its assumptions, include a reproducible check, and pass code quality and review. An unsupported tax rule or missing product term must be visible; it must not silently become a zero tax rate or guaranteed return.

## Run locally

```sh
mkdir -p .cache/uv .runtime/tmp
export UV_CACHE_DIR="$PWD/.cache/uv"
export UV_PYTHON_INSTALL_DIR="$PWD/.runtime/python"
export TMPDIR="$PWD/.runtime/tmp"
uv sync --frozen --dev --extra benchmarks
uv run --frozen --extra benchmarks streamlit run app.py
```

Open the localhost address printed by Streamlit. The Household page starts with an explicitly synthetic example; edit the tables and select **Validate and project**. Keep a baseline to compare a clone. The Annual tax page edits standalone federal/NJ cases. Enable Household tax assumptions in the household form to include annual recognition, withholding, estimated payments, December settlement, delayed refunds and optional permitted taxable-account sales. The editable starter assumes wages and frozen 2025 law; review its mappings and annual cases. See [tax cash-flow conventions](docs/adr/0003-tax-cash-flow.md). See [tax coverage and limits](docs/tax-rules.md). The Tax lots page provides dated trade accounting, FIFO/HIFO/specific selection, separate bases and an optional sale-decision form with explicit current prices; choose the **Harvesting comparison** synthetic example to compare holding and exit outcomes. [Its documented scope](docs/adr/0004-lots-and-harvesting.md) distinguishes conditional annual tax savings from household cash benefits. The Retirement page starts with a synthetic high-earner case and shows requested versus funded contributions, deductions and basis. [Contribution coverage](docs/adr/0005-retirement.md), [forward rule assumptions](docs/adr/0016-future-contribution-assumptions.md) and [IRA withdrawal coverage](docs/adr/0006-ira-withdrawals.md) list supported rules and unfinished layers. Switch the Retirement workbench to IRA withdrawals for dated cash, basis and conditional annual tax results, HSA for [cash funding and receipt checks](docs/adr/0007-hsa.md), Education for [529 funding and annual expense allocation](docs/adr/0008-education.md), Medicare for [IRMAA history and premium funding](docs/adr/0009-medicare.md), or Social Security for [ordinary claims and reference comparisons](docs/adr/0010-social-security.md), including [dated survivor cases](docs/adr/0011-survivor-benefits.md). The Household page can load a synthetic retired household and edit [generated benefit cash/tax assumptions](docs/adr/0012-household-social-security.md). The Household page also loads a [synthetic employment path](docs/adr/0013-employment-wages.md) and edits dated work choices alongside salary/bonus streams and retirement dates. Load the synthetic employer-compensation or linked-shock household to inspect [tranche value, liquidity and independent tax allocations](docs/adr/0014-employer-compensation.md). Load the synthetic IRA household to edit [fixed withdrawal/conversion schedules and annual reconciliation](docs/adr/0015-household-ira.md). Load the synthetic Medicare household to inspect [conversion-driven lookback premiums and cash arrears](docs/adr/0017-household-medicare.md). The Engine checks page runs independent numerical cases. See [cash-flow conventions](docs/adr/0002-household-cash-flow.md) for current limits. The optional `benchmarks` extra adds Owl and its solver dependencies. See [development setup](docs/development.md) for cache locations and Intel-Mac build prerequisites, and [executed reuse checks](docs/reuse-results.md) for what has actually been validated.

Original work is GPL-3.0-or-later; see [LICENSE](LICENSE). Third-party dependencies retain their own licenses.

Load the synthetic Social Security with Medicare withholding household to inspect [current-premium collection and its explicit scope](docs/adr/0018-household-benefit-premiums.md).

Load the synthetic employee 401(k) household to inspect [gross payroll, pretax wage exclusions, Roth elections and current-payroll funding](docs/adr/0019-household-employee-deferrals.md).

In IRA withdrawals, choose Contributions with withdrawals for [combined current-year funding and basis reconciliation](docs/adr/0020-current-year-ira-deposits.md); the [household adapter](docs/adr/0021-household-ira-deposits.md) now funds confirmed deposits from actual cash.

Load the synthetic IRA contribution household for [actual deposit funding, carried basis and completed tax eligibility](docs/adr/0021-household-ira-deposits.md).

Load the synthetic cash HSA household for [actual HSA funding, historical receipt carry and conditional NJ recognition](docs/adr/0022-household-cash-hsa.md).

Load the synthetic 529 tuition household for [qualified institution payments, cash fallback and actual NJBEST deductions](docs/adr/0023-household-education.md).

The Markets workspace generates and exports [realized market batches](docs/adr/0024-paired-market-paths.md); its factor charts do not yet measure household spending safety.

Load the synthetic actual-lot funding household for [actual share sales, separate basis and household tax cash](docs/adr/0025-household-lot-funding.md). This bounded profile replaces proportional-basis selling for linked accounts; remaining harvesting/year-end/distribution adapters are unfinished.

Load the synthetic January wash reconciliation household for [original-year loss recognition, dated tax positions and completed wrapper checks](docs/adr/0026-january-wash-reconciliation.md). Default pending-December blocking remains available.

In Markets, select **Household funding** to run [actual taxable-lot funding on identical realized paths](docs/adr/0027-household-market-execution.md), with separate yield tax, liquidity locks, selected spending inflation and supplied-horizon outcomes. The default synthetic horizon is two years and does not establish retirement safety.

Markets / Household funding can load an [adjustable synthetic discretionary guardrail](docs/adr/0028-discretionary-spending-guardrails.md). Observed wealth triggers a bounded cut/restoration; actual spending reductions stay separate from funding success.

Markets / Household funding offers [actual staged/concentration sales and conditional replacement harvesting](docs/adr/0029-household-sale-harvest-policies.md). Policies use current monthly marks, actual household cash/taxes and existing lot selection; tax-budget forecasts and broader rebalancing remain separate work.

Markets / Household funding also offers [ordinary IRA and 529 return proxies](docs/adr/0030-wrapper-market-paths.md), including wrapper-only runs, actual dated withdrawal/tuition consequences, outgoing liquidity restrictions and explicit issuer-concentration coverage.

Markets / Household funding offers [employer net factors with conditional employment linkage](docs/adr/0031-employer-market-employment.md). Observed drawdowns can trigger next-month job loss, explicit rehiring and supplied forfeiture, while independent tax allocations and payout rights remain in the existing tranche ledger.

Markets / Household funding also offers [employee 401(k) investment proxies](docs/adr/0032-workplace-investment-returns.md). Actual payroll-funded pretax/Roth deposits earn explicit month-end returns inside the plan, with unchanged wage/payroll recognition and separate investment audits; broader workplace withdrawal adapters remain unfinished.

The **Products** workspace now compares [long/short pre-tax economics and margin risk](docs/adr/0033-long-short-economics.md) with a separately configured unlevered reference on identical paths. Short collateral, loans, actual costs and blocked/forced exits remain visible. A separate [conditional private-fund contract](docs/adr/0060-conditional-private-fund-contracts.md) adds investor cash/basis rules; broader legal eligibility and automatic trade/basis recognition remain unfinished.

Load the synthetic long-short household, or select **Long-short household** in Markets / Household funding, for [actual collateral, redemptions and recourse-debt integration](docs/adr/0034-household-long-short-cash.md). Taxes use separately supplied recognition; automatic trade tax/basis remains unfinished. The separate conditional private-fund contract adds independently supplied outside basis and cash-only exit assumptions.

Markets / Household funding / Long-short household also offers [independent conditional federal/NJ loss recognition](docs/adr/0035-conditional-sleeve-loss-recognition.md). Positive income stays recognized; denied, deferred and allowed supplied losses keep separate dates/character and never create a tax-savings cash receipt. This does not calculate legal eligibility or basis.

The annual tax form and household tax-character rules support [explicit positive ordinary noninvestment income](docs/adr/0036-ordinary-noninvestment-income.md), with a disclosed numerical adapter and separate federal/NJ classification. It does not infer business-loss, private-fund or HSA-distribution eligibility.

Load the synthetic nonqualified HSA household for [actual funded distribution taxes](docs/adr/0037-household-hsa-distribution-tax.md), including qualified receipt matching, separately displayed additional tax and independent declared federal/NJ recognition assumptions. This cash-bank profile does not infer historical state basis or pay new medical bills.

Retirement / **OWL household reference** compares a solved independent withdrawal policy with [actual monthly household cash, separate IRA basis and annual taxes](docs/adr/0038-owl-household-reference.md). Tax-forecast differences, source heirs-tax assumptions, native funding/RMD shortfalls and the wealth/tax residual remain visible and exportable; it is not the personal optimizer.

Load **synthetic current medical bills** in Household for [actual HSA provider payments, cash fallback, arrears and paid-only shared receipts](docs/adr/0039-current-medical-bills.md). Automatic medical deductions, insurance recovery and invested-HSA state basis remain unfinished.

Markets / Household funding / **Medical bill inflation** adds [dated cost forecasts and fixed-versus-indexed HSA election bounds on identical CPI paths](docs/adr/0040-medical-bill-market-inflation.md). The synthetic matched case has equal ending wealth but different ability to pay the bill; indexed forecasts do not create reimbursement receipts.

Retirement / **HSA investments** adds [dated inside-HSA lot accounting](docs/adr/0041-invested-hsa-book.md), current-price cash targets, custodian fees and independently supplied conditional NJ basis. Recipient distributions and household integration remain separate work.

Load **synthetic invested HSA household** for [actual medical and withdrawal funding from permitted share sales](docs/adr/0042-household-invested-hsa.md), separate marked assets and cash, actual conditional NJ recognition and carried basis/fee obligations. Payroll funding and automatic medical deductions remain separate work.

Markets / Household funding / **Invested HSA** runs [actual positions, yield, sale locks, medical funding and conditional NJ recognition on shared realized paths](docs/adr/0043-invested-hsa-market-paths.md). Price appreciation stays distinct from taxable realized gains and cash income.

Load **synthetic payroll HSA household** for [qualifying section125 salary reductions sharing actual wages, employee401k room and HSA eligibility](docs/adr/0044-household-payroll-hsa.md). Salary reductions, personal deductions and external employer funding remain distinct; conditional NJ liability and withholding use independent wage treatment.

Markets / Household funding / **HSA payroll and employment** adds [automatic matched salary-versus-personal funding controls under observed employer shocks](docs/adr/0045-hsa-funding-employment-comparison.md). Actual funded deposits, reported taxes, dated payments/refunds and cash availability remain separate; the control uses submitted inputs and the same realized paths.

Load the synthetic pension with source withholding household for [net receipt, actual tax credit and delayed refund reconciliation](docs/adr/0046-source-withholding.md). Only net cash can fund optional wrapper deposits.

Load the synthetic 401(k) cash withdrawals household for [actual gross plan debits, net receipts and separation-age tax treatment](docs/adr/0047-workplace-cash-withdrawals.md). This ordinary zero-basis profile rejects RMD years and special distributions; broader workplace withdrawals and rollovers remain in progress.

Load the synthetic separate-plan RMD household for [complete plan groups, required/eligible withholding portions and actual December catch-up](docs/adr/0048-workplace-rmd.md). Shortfalls retain explicit contingent excise and unresolved-prior-year status; broader retirement adapters remain in progress.

In Markets, select **Workplace RMDs** for [the same plan requirements on realized paths, explicit illiquidity failures and matched catch-up policies](docs/adr/0049-workplace-rmd-market-paths.md). Required transfers and their shortfalls remain separate from ordinary spending cash.

Retirement / IRA withdrawals / **Direct plan rollover with withdrawals** adds [confirmed incoming qualified-plan cash and independently supplied federal/NJ basis](docs/adr/0050-incoming-ira-rollovers.md). Received IRA assets create no spending cash or ordinary contribution deduction; actual household source transfers remain the next retirement adapter.

Load **synthetic direct plan rollover** in Household for [actual separated-plan debits feeding the same-owner IRA ledger before withdrawals](docs/adr/0051-household-plan-rollovers.md). Source locks, current/prior RMD blocks and unfilled requests remain visible; zero-basis ordinary direct cash transfers create no spending receipt or contribution deduction.

Markets / Household funding / **Direct plan rollovers** adds [actual source and IRA execution on shared realized paths](docs/adr/0052-plan-rollover-market-paths.md), per-path funded/unfilled transfers and matched policy comparisons. The two-year synthetic horizon and ordinary zero-basis transfer limits remain explicit.

Load **synthetic designated Roth plan cash** in Household for [complete plan-contract cost pools, participation clocks, ordinary cash and actual payroll cost additions](docs/adr/0053-designated-roth-plan-cash.md). Federal pro-rata recognition stays separate from IRA ordering; independent NJ cost and its conditional treatment remain explicit.

Markets / Household funding / **Designated Roth plan cash** runs [actual contract cost, taxable earnings and outgoing restrictions on realized paths](docs/adr/0054-designated-roth-market-paths.md). Optional unfilled cash requests and independently conditional NJ recognition stay separate from mandatory spending outcomes.

Products / **Traditional exchange funds** now compares an [explicit conditional synthetic contract](docs/adr/0080-traditional-exchange-funds.md) with actual direct sales on common price marks: partial source contribution, independent retained bases, fees/distributions, blocked or supplied-tax early exits, basket release, eventual taxable sale and actual household spending/tax funding. Eligibility and sponsor terms remain unverified inputs; deferral is not elimination. Entered, deterministic, downside-stress and selected seeded Monte Carlo price paths are editable and exportable.

Products / **Conditional private fund** adds [actual household cash, settlement gates and independent outside-basis/exit assumptions](docs/adr/0060-conditional-private-fund-contracts.md), compared with an independently configured unlevered tax proxy on identical realized paths. Denied/deferred/allowed federal and NJ losses remain independent; pending interests and settlement claims stay visibly incomplete. Investor eligibility, limited liability and the cash-only no-hot-assets/no-liability-change profile require explicit assumptions; no provider terms or legal eligibility are inferred.

Retirement / **Social Security with employment** adds [own-record work-test forecasts and closed-year settlement](docs/adr/0055-social-security-work-test.md). Whole-check withholding, later refunds/debt and reduction-factor arrears remain distinct, with conditional collection dates and frozen2026 wage limits. Household/tax and auxiliary-record work effects remain unfinished.

Load **synthetic Social Security with earned wages** in Household for [actual gross-payroll work tests, receipt-year net benefits and carried government claims/debt](docs/adr/0056-household-social-security-work.md). Separate forecasts preserve earlier cash after later wage surprises; unpaid claims affect net wealth but cannot fund spending. The explicit own-record scope and conditional collection/processing assumptions remain editable.

Markets / Household funding / **Taxable rebalancing** adds [dated target allocations funded by actual lot-sale proceeds](docs/adr/0057-observed-taxable-rebalancing.md). Edit weights, drift bands, sale caps and commissions; compare against a matched hold policy on the same paths. Remaining drift, costs, locks, actual taxes and spending shortfalls stay visible.

Products / **Options overlays** runs [dated covered calls, collars and four-leg stock/index scenarios](docs/adr/0070-dated-options.md), QuantLib model marks, actual exercise/assignment cash/share/basis changes, configured collateral, separate tax uncertainty and hypothetical complete unwind. The stock/index stress grid values every leg; no aggregate floor or historical return series is inferred.

Load **synthetic actual option household** in Household for [premiums, share delivery, reserved collateral and unreserved proceeds sharing actual spending cash](docs/adr/0071-household-options.md), with actual basis-driven federal/NJ recognition and annual tax settlement. Explicit dated monthly marks are required; Markets now offers a bounded shared-path option profile, with unsupported quote periods and liquidity paths guarded.

Markets / Household funding / **Options household** executes [covered calls, collars and four-leg contracts on the same realized stock/index paths](docs/adr/0072-options-market-paths.md), with separate supplied model-pricing assumptions, actual spending/tax cash and all-mark product feasibility. No historical option quote series or aggregate protection floor is inferred.
Products / **Whole-life illustrations** imports and audits [supplied guaranteed/current/stressed policy schedules](docs/adr/0100-supplied-whole-life-illustrations.md), with JSON and CSV inputs, dated cash-value/surrender/death returns, explicit loan debt, unknown stop-funding values and premiums due after retirement. The contract and Household adapters below add conditional taxes and actual funding; the matched comparison is described below.

Products / **Whole-life contract cash and taxes** adds [executed policy cash, loan/basis accounting and conditional annual liability](docs/adr/0102-whole-life-contract-cash-and-tax.md), including a zero-cash taxable lapse, MEC assumptions and independently supplied NJ recognition. This standalone view assumes events already executed and funded; the Household adapter below applies actual funding.

Load **synthetic whole-life household** in Household for [actual required premium funding, dated reserves and independent insurance needs](docs/adr/0103-household-whole-life-funding.md). Policies share cash, permitted tax-lot sales and annual taxes; unfunded payments use supplied conditional exits, while loan debt reduces net surrender equity once. Retirement premiums, withheld cash and protection gaps stay visible. Policy values remain supplied conditional paths; the matched comparison is described below.

Products / **Whole life versus liquid saving** compares [matched limited/longer premium schedules or an existing policy with liquid saving and independently priced term cover](docs/adr/0104-insurance-and-liquid-saving-alternatives.md). All alternatives retain the same household capital, spending, tax background and realized market paths. Actual shares, surrender taxes, cash reserves, retirement premiums and protection gaps are reported separately. Marked wealth excludes unexecuted future exit taxes; short synthetic examples are not retirement-safety conclusions. Individual alternatives export directly to Household.

Load **synthetic scheduled liquid saving** in Household to edit actual month-end investment budgets, commissions, allocations and cash buffers in the linked-lot form. Unfilled optional saving remains distinct from required-payment failures.

The **Optimize** workspace now searches [finite allowed retirement, sale/harvest, IRA and funding-order policies](docs/adr/0130-bounded-household-policy-search.md), with lockable choices and discretionary guardrails. All candidates share one training market batch; the selected policy is frozen before a separate validation sample. Spending safety and reserves precede after-tax exit wealth. The short starter deliberately fails the default age-100 horizon, and unsold assets cannot masquerade as after-tax exit proceeds. Product allocation and broader wrapper/cross-border integration remain required before the optimizer ticket is complete.

Optimize can add [matched deterministic, historical and named-stress checks](docs/adr/0131-frozen-policy-robustness.md) for the frozen selected policy and original baseline. Required failures affect configured validation; optional failures remain visible. Scenario-path fractions are not probabilities, and stochastic-stress intervals are explicitly conditional. The existing early-crash, prolonged-inflation, concentration-loss and illiquidity starters are available with editable assumptions.
