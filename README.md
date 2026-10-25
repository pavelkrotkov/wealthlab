# Wealthlab

A local-first financial scenario workbench. **Early implementation: household editing, monthly cash-flow comparison, a separate annual federal/NJ tax workbench and engine checks run locally. Optional household tax cash flows and permitted taxable-account funding now run. State-tax payment deductions and conditional refund recognition are included. The Tax lots page adds lot accounting, optional federal/NJ wash scenarios, dated retain/sell/staged/concentration/tax-budget policies and conditional annual liability comparisons; matched long-only harvesting comparisons and a hypothetical taxable-account exit. Dated recurring fees distinguish paid/owed cash charges from embedded-price estimates. Distribution entitlements, receipts and conditional dividend qualification feed annual tax comparisons. Current-loss attribution separates own/external gain use, ordinary consumption and carry from actual liability differences. The Retirement workspace adds dated 2025/2026 IRA and employee 401(k) contribution allocation, cash shortfalls and separate federal/NJ basis additions. Explicit frozen-2026 assumptions now permit future-year contribution/HSA cases while preserving actual calendar ages and eligibility. Employee 401(k) elections now share household payroll cash and tax recognition while preserving gross payroll wages and explicit workplace/IRA account identity. The annual IRA workbench now combines current-year deposits with withdrawals/conversions, using one cash book, separate basis additions and supported completed-tax eligibility checks. The retirement workbench includes conditional IRA withdrawals/conversions, basis reconciliation, Roth clocks and required-withdrawal targets. Confirmed optional IRA deposits now use actual household receipts and carry basis, with completed eligibility checked after tax funding. Fixed ordinary-IRA schedules feed household cash, balances and December tax reconciliation with carried federal/NJ basis and Roth histories; in-year figures omit unfinalized IRA tax. The HSA cash layer adds monthly family/Medicare limits and shared medical-receipt tracking; confirmed household cash HSAs now share actual deposits, federal deductions and historical qualified reimbursements under explicit conditional NJ bank assumptions. Nonqualified household distributions now use explicit funded tax assumptions. Current medical bills now use actual HSA/cash payments and carried unpaid liabilities; Confirmed invested HSAs now share actual securities, cash funding and explicit conditional NJ basis; market paths now support confirmed price/yield/liquidity bindings. The Education layer adds savings-type 529 funding, explicit higher-education expense allocation, separate tax recipients and conditional NJBEST history; qualified household institution bills now use actual 529 funding, cash fallback and completed-income NJBEST deductions. Other distribution purposes and household tax adapters remain unfinished. The Medicare layer adds explicit income lookback, conditional future premiums and dated cash shortfalls; direct-billed premiums now share household healthcare cash, arrears liabilities and completed-return lookbacks; the Social Security layer adds ordinary own/spouse claims, exact month/credit timing and limited Owl comparisons; dated survivor claims, inherited delayed credits and survivor-to-own switches now run; generated all-survive claim cash now enters household cash and federal/NJ taxes under explicit scope guards. A confirmed current-premium profile now separates gross SSA recognition, net cash and Medicare withholding with per-record rounding. Work-test rules, dated-death household accounting, other collection profiles, wrapper funding and broader integration remain unfinished. Household employment paths now include dated reduced pay, job loss and rehiring; conditional employer tranches now separate grants, net growth, vesting, forfeiture, cash rights and supplied tax allocations, including a reproducible linked employment/asset shock. Legal classification, basis and hypothetical exit tax remain unmodeled. The Markets workspace generates reproducible deterministic, historical, correlated Monte Carlo and named stress batches; household path/lot integration, spending success, product strategies and optimization remain in progress.**

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

The **Products** workspace now compares [long/short pre-tax economics and margin risk](docs/adr/0033-long-short-economics.md) with a separately configured unlevered reference on identical paths. Short collateral, loans, actual costs and blocked/forced exits remain visible; private-fund contracts, eligibility and complete tax/basis recognition remain unfinished.

Load the synthetic long-short household, or select **Long-short household** in Markets / Household funding, for [actual collateral, redemptions and recourse-debt integration](docs/adr/0034-household-long-short-cash.md). Taxes use separately supplied recognition; automatic trade tax/basis and private-fund contracts remain unfinished.

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
