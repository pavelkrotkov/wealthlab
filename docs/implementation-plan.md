# Implementation plan and draft tickets

October 23, 2026. Feature scope is confirmed; this breakdown awaits review before GitHub issue publication. Every feature includes editable inputs, a callable calculation path, UI results, import/export where relevant and a reproducible acceptance case. No ticket is complete merely because a schema or placeholder exists.

## Delivery order

| ID | Demoable slice | Type | Depends on |
|---|---|---|---|
| 01 | Reuse spikes and repository quality gates | AFK, except provider secret | None |
| 02 | Save, edit and compare a household cash-flow scenario locally | AFK | 01 |
| 03 | Explain annual federal and NJ tax and settle it in cash | AFK | 02 |
| 04 | Compare concentration reduction with tax-lot harvesting | AFK | 03 |
| 05 | Plan retirement-account withdrawals, conversions and benefits | AFK | 03 |
| 06 | Project employment, vesting and employer-fund liquidity | AFK | 03 |
| 07 | Run matched historical, stochastic and stress comparisons | AFK | 04, 05, 06 |
| 08 | Compare leveraged long/short and private tax-aware funds | AFK | 04, 07 |
| 09 | Compare covered calls, collars and synthetic exposure | AFK | 04, 07 |
| 10 | Compare a traditional exchange fund and its exit basket | AFK | 04, 07 |
| 11 | Project opportunity-zone fund cash flows and tax dates | AFK | 03, 07 |
| 12 | Project drilling-partnership cash flows and deduction limits | AFK | 03, 07 |
| 13 | Compare whole-life illustrations with liquid alternatives | AFK | 03, 07 |
| 14 | Evaluate Puerto Rico residency and incentive assumptions | AFK | 03, 04, 06 |
| 15 | Evaluate Spanish regional income and wealth taxes | AFK | 03, 04, 05 |
| 16 | Reconcile cross-border moves, FX and overlapping taxes | AFK | 14, 15 |
| 17 | Search bounded policies and compare spending safety | AFK | 07–13, 16 |
| 18 | Package and validate the complete local workbench | AFK | 17 |

AFK means the feature can be implemented with synthetic cases without further personal information. It does not authorize assuming a household's legal eligibility. Missing private inputs stay unset. Actual product terms can later replace conditional assumptions without requiring a code change.

## 01 — Reuse spikes and repository quality gates

Build a minimal synthetic UI that runs one representative case through candidate libraries. Adopt only the packages that pass; record version, license, input mapping and limitations. Establish CI and exact-head J-Bot review.

Acceptance:
- Run federal-tax, retirement-optimizer and option-pricing spikes on a supported local Python version; preserve independent expected values and timing.
- Inspect and test NJ coverage before choosing PolicyEngine or a focused custom implementation. Benchmark before committing to an integration architecture.
- Enforce CC <= 8, MI >= 50, module SLOC <= 300 and function span <= 60; prove each gate rejects a deliberately failing synthetic example.
- Ruff, format, type checking, tests/coverage, dependency audit, actionlint and zizmor run on stacked PRs regardless of base branch.
- J-Bot uses pinned action, authorized comment trigger and a frozen head; provider errors fail visibly. List secret names only, never values.
- Required-check protection is enabled after the bootstrap checks exist. Setup cannot be called complete without an observed bot review.

## 02 — Local household scenario editor and cash-flow comparison

Enter two household members, dates, accounts, currencies, expenses, debts and income. Save/reload a scenario and compare it with a clone after changing retirement timing or spending.

Acceptance:
- Versioned, validated schema rejects non-finite values, impossible dates, duplicated identifiers and inconsistent units; critical unknowns are not coerced to zero.
- Monthly cash-flow ledger includes income, contributions, spending, fees, debt principal/interest and balances. Show nominal and real dollars distinctly.
- Handle partial first year and year-to-date income/taxes without counting them twice.
- Separate essential/discretionary/healthcare/education/mortgage budgets, inflation assumptions and liquid reserves.
- Private files are read/written only to selected paths, with atomic save and no silent overwrite. Synthetic examples are obvious.
- Round-trip export reproduces results; no-return/no-tax examples reconcile exactly to cash flows. UI labels this slice's tax support as incomplete until 03.

## 03 — Federal and New Jersey tax reconciliation

Compare working and retired scenarios with annual tax breakdowns tied to income events and payment cash flows.

Acceptance:
- Ordinary income, qualified dividends, ST/LT/collectibles gains, retirement income, payroll taxes, NIIT and itemized/standard deductions have explicit mappings and supported-year labels.
- Federal carryforwards and NJ disposition/partnership categories and jurisdiction-specific basis remain separate; include deduction limitations relevant to supported cases.
- Aggregate household income once and reconcile liability, withholding, estimated payments and balance due. Solve withdrawal-induced tax cash needs without inventing financing.
- Future policy projection states known versus assumed parameters; unsupported combinations block or prominently qualify affected results.
- Independent hand/form/package comparisons cover tax brackets, mixed gain/loss characters, carry use and category differences; current official authorities are cited by year.

## 04 — Concentration, sale policies and tax-loss harvesting

Compare retain, immediate sale, staged shares, target concentration and tax-budget policies, with ETF/completion/direct-index sleeves and matched harvesting-off controls.

Acceptance:
- Actual or synthetic lots support acquisition dates and federal/NJ bases; specific-lot/HIFO selection never oversells.
- Selling a fraction of original shares differs from reaching a portfolio weight or reducing economic exposure.
- Realized losses update basis and carry ledgers; household/spouse/retirement-account wash interactions and replacement restrictions are explicit.
- Transaction costs, distributions, advisor/manager/custody fee bases and terminal liquidation are applied consistently.
- Lot quantity/basis and cash conservation checks; partial sales, replacement purchases, no available losses and locked securities cases.
- Show gross losses, recognized losses, own-gain use, external-gain offsets, carry, deferral and remaining concentration separately.

## 05 — Retirement wrappers, benefits and education accounts

Project traditional/Roth/HSA/education accounts, contributions and withdrawals with editable benefit dates and conversions.

Acceptance:
- Annual wages, contribution eligibility/limits, RMDs, early-access rules and Roth basis/conversion clocks use dated inputs and rule provenance.
- Social Security claiming, spouse/survivor cases and Medicare/IRMAA history are included; healthcare and education cash needs cannot be paid from ineligible wrappers without modeled consequences.
- Distinguish retirement-account tax basis across jurisdictions; do not assume all distributions are fully taxable everywhere.
- Compare supported cases with OWL while explicitly reporting differences in scope. Own ledger remains authoritative for lots and unsupported OWL cases.
- UI can lock conversion/withdrawal schedules and displays unmet spending rather than negative hidden balances.

## 06 — Employment and employer-linked compensation

Compare continue working, reduced pay, job loss and retirement with dated salary/bonus and employer-linked asset events.

Acceptance:
- Separate grant, economic growth, vesting, forfeiture, cash distribution and taxable allocation. Events specify owner and tax character.
- Tax-distribution election changes cash and the affected balance exactly once; allocated income may be taxable without cash.
- Tranche schedules and employer-linked concentration feed liquidity and funding checks.
- Optional joint employment/asset stress is explicit and reproducible; no unsupported causal probability is assumed.
- Private plan terms remain user inputs with provenance; invalid combinations generate clear diagnostics.

## 07 — Matched market paths and stress analysis

Run deterministic, historical, correlated Monte Carlo and named stress modes against the same household policies.

Acceptance:
- Asset-specific return, dividend/yield, volatility, correlation and inflation assumptions; validate covariance and units.
- Preserve sequence risk, seeded reproducibility, paired paths and uncertainty intervals for simulated success estimates.
- Historical inputs include provenance, total-return conventions and coverage checks; no silent future data or missing-price filling.
- Crashes, inflation, employer correlation and illiquidity stresses report funding failure timing and magnitude, reserve breaches, drawdown and concentration.
- Rebalance/guardrail decisions use information available at the date. Do not optimize separately with knowledge of each future path and call that achievable performance.

## 08 — Leveraged long/short and private tax-aware funds

Compare a configurable long/short sleeve and a separate conditional private-fund model with unlevered investments.

Acceptance:
- Gross/net exposure, short borrow, financing, turnover, fees, redemptions and liquidation cash flows are visible.
- Tax benefits have denied/deferred/allowed cases; capital versus ordinary character and federal/state limitations are independent.
- Exposure and losses are economically linked; user-prescribed loss schedules are labelled assumptions rather than generated alpha.
- Leverage and liquidity failures feed household safety. No provider return or tax representation is implied.

## 09 — Options overlays and synthetic exposure

Build date-specific covered-call, collar and four-leg synthetic exposure scenarios with leg-level P&L and household cash needs.

Acceptance:
- Explicit strikes, expiries, quantities, multipliers, premiums, dividends, fees, exercise style, settlement and roll rules; use QuantLib where appropriate.
- Exercise/assignment changes shares, cash and basis; collateral and broker-rule assumptions are configurable and visibly conditional.
- Show stock/index two-dimensional stress, mark-to-market and complete unwind; no aggregate floor inferred from one protected leg.
- Recognition, straddle deferral, covered-call qualification, constructive-sale assumptions and section 1256 classifications have reviewed rule paths or explicit conditional treatment.
- No double counting premiums; expiry payoff checks and independent valuation examples; unsupported quote periods cannot yield fabricated historical returns.

## 10 — Traditional exchange funds

Compare contribution, lockup, fees, distributions and exit baskets with direct sales using a synthetic contract specification.

Acceptance:
- Contribution/acceptance assumptions, retained basis, liquidity limits and redemption timing are explicit.
- Model basket allocation and eventual taxable exit; distinguish deferral from permanent elimination.
- Early redemption and household cash-shortfall stresses; missing sponsor terms are visible.

## 11 — Opportunity-zone funds

Compare dated eligible-gain reinvestment and fund cash flows with a liquid alternative.

Acceptance:
- Effective-date tax regime, eligibility clock, gain inclusion date, basis events and exit tests are parameterized from verified authorities.
- Capital calls, debt, fees/carry, distributions and exit delays produce cash flows; preferred return is not a guaranteed yield.
- Taxes can fall due without sufficient distribution; show household funding impact.
- Denied qualification/benefit and delayed-exit cases are compared with the same underlying investment economics.

## 12 — Drilling partnerships

Project contribution, production cash flows, expenses, depletion/recapture and exit under explicit commodity and deduction assumptions.

Acceptance:
- Ordinary/capital/passive, basis, at-risk and jurisdiction-category limitations are distinct.
- GP/LP liability/eligibility assumptions are displayed; no liability risk is represented as a guaranteed bounded investment loss.
- Denied/deferred deductions and poor production cannot appear profitable merely from headline tax savings.
- Matched after-tax cash-flow and terminal comparison with liquid investments.

## 13 — Whole-life illustrations and insurance alternatives

Import guaranteed/current/stressed illustration schedules and compare limited-pay and long-duration premiums with liquid saving and separately priced protection.

Acceptance:
- Premium, cash/surrender value and death benefit are separate; calculate money-weighted cash-value returns from actual timing.
- Model loan principal/interest, withdrawals, surrender/lapse and conditional MEC tax consequences; stop-funding years are configurable.
- Missing contract values remain unknown; no dividend-interest rate is substituted for policy IRR.
- Household spending reserve and post-retirement premium obligations are visible; insurance need is an input, not inferred from investment balances.

## 14 — Puerto Rico

Provide a residency/income-source/incentive configuration and compare it against the mainland baseline.

Acceptance:
- Separate US federal and Puerto Rico computations and credits; validate dates, source, bona fide-residency and incentive assumptions against current primary authorities.
- Track pre-move appreciation and relevant income categories instead of applying a blanket zero rate.
- Unconfirmed eligibility prevents an unconditional benefit claim; ordinary and denied-incentive alternatives remain runnable.
- Independent boundary and move-year tests plus dated legal sources.

## 15 — Spain

Provide a Spanish residency and autonomous-community scenario with income and wealth-tax views.

Acceptance:
- Separate general/savings income bases, ownership, deductions, regional income rules, wealth and solidarity taxes and relevant exemptions/credits, with effective-year provenance.
- Explicit treatment assumptions for US retirement/insurance/partnership products; unsupported classification blocks the affected result.
- Currency translation and valuation dates are explicit; property and debt enter the appropriate bases.
- Independent official-example/regional boundary tests. Region is required where it changes the result.

## 16 — Cross-border moves and tax interactions

Compare dated moves among supported jurisdictions without counting tax credits or exemptions twice.

Acceptance:
- Person-specific status, sourcing, residency periods, treaty assumptions, foreign tax credit baskets/timing and FX are explicit and validated.
- Full-year versus part-year treatment follows each supported jurisdiction rather than a global December-31 switch.
- Carryovers, basis differences, pre-move appreciation and departure/arrival effects remain auditable.
- Show total household taxes by jurisdiction, cash-payment timing and unresolved legal assumptions; unknown facts cannot silently select favorable eligibility.

## 17 — Bounded policy search and spending safety

Search allowed retirement dates, sale/harvest policies, conversion schedules, withdrawal order and product allocations; compare feasible candidates.

Acceptance:
- User-set bounds and locks; fixed spending and optional discretionary guardrails. Essential spending is never silently reduced.
- Default configurable 95% simulated funding success, younger-spouse age-100 horizon and two-year reserve; display model dependence and sample uncertainty.
- Optimize spending feasibility first, after-tax wealth second, while showing taxes, concentration, liquid capital and downside separately.
- Search and validation paths are separated to reduce overfitting; rank only comparable, supported cases and expose infeasible constraints.
- Report best evaluated candidate, search coverage, seed and solver status; no global-optimum claim without evidence.
- Blend sleeves without duplicating capital, losses, fee bases or liquidity. Every discussed product can participate conditionally within explicit constraints.

## 18 — Complete local workbench release

Ship a reproducible installation, launch command and documented scenario workflow on the selected Mac.

Acceptance:
- All prior slices demonstrated in the UI using synthetic fixtures; CLI and UI calculations agree.
- End-to-end local save/import/export, compare, optimize, audit and reproduce tests; browser accessibility and keyboard smoke checks.
- No private data or credentials in git/history/logs; no implicit outbound scenario transmission; loopback binding and safe import/path handling.
- Dependency/license notices, source provenance and known limitations are current. Unsupported combinations are discoverable before running.
- Green required checks and observed J-Bot reviews on current PR heads; findings resolved with evidence.
- Deliver a short user guide, model coverage matrix and a private input checklist. Completion does not require inventing missing personal data.

## Review and stack strategy

Start with foundation/research, then foundation/quality. After foundation lands, each feature is a small vertical stack or PR, with dependent sublayers only when review size requires it. Tests for each behavior travel with that behavior. Independent feature stacks branch from the same verified base; do not put unrelated work in a linear dependency chain.

Two review rounds: request review, address findings and CI, then review the updated head. Merge only the exact reviewed/check-passing head. Bot unavailability is an explicit setup issue, not a successful review. The provider credential is human setup if it cannot be supplied through an already authorized local secret mechanism.
