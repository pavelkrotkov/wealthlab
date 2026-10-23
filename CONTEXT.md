# Domain and scope

Decisions recorded October 23, 2026. This document contains generalized product requirements, not a household financial inventory.

## Confirmed product decisions

- Local browser UI and local calculation engine. Public code; private scenario files.
- Primary objective: sustainable after-tax spending and downside protection; secondary objective: after-tax wealth within risk, concentration and liquidity constraints. Tax paid is a separate diagnostic.
- Adjustable starting targets: 95% simulated funding success through age 100 of the younger spouse, plus two years of liquid spending reserve. These are configuration defaults, not validated probabilities or recommendations.
- Optimize retirement date, sale timing, harvesting, Roth conversions, withdrawal order and strategy allocation, with explicit user-set bounds and locks.
- Both fixed real spending and optional discretionary spending guardrails. Separate essential, discretionary, healthcare, mortgage and education expenses.
- Employment paths include salary/bonus, job loss, reduced earnings, retirement, vesting, forfeiture, employer investment performance and tax distributions. Correlated employment/employer-asset shocks are supported.
- Deterministic assumptions, historical replay, correlated Monte Carlo and named stresses; matched comparisons share paths and seeds.
- Editable forms and CSV/JSON import/export, including lots and product cash-flow illustrations. No live brokerage integration in the first complete version.
- US federal, New Jersey, Puerto Rico and Spain residency scenarios, configurable by person, year, region and effective date. Eligibility and legal treatment are explicit inputs with validation, not inferred from a place name.
- Include conditional models for every product family below. Distinguish allowed, deferred and denied tax benefits; compare liquidity and complete-exit economics.

## Account and instrument coverage

Cash and reserves; taxable brokerage; concentrated stock; diversified equities/bonds; gold/collectibles; traditional retirement accounts; Roth accounts; HSA; education accounts; property and debt; deferred/employer compensation and partnership interests.

Strategies: retain, immediate sale, staged sale, tax-budget sale, concentration-target sale, completion portfolio, long-only direct indexing/TLH, leveraged long/short harvesting, private tax-aware funds, traditional exchange funds, covered calls, collars, synthetic market exposure/EFR, opportunity-zone funds, drilling partnerships, limited-pay and long-duration whole life. Blended allocations must conserve household capital.

## Vocabulary and accounting rules

- **Scenario**: immutable inputs, policy choices, market path configuration and tax-rule version.
- **Fact / assumption / illustration / unresolved**: distinct input provenance states. Unresolved critical inputs block a personalized conclusion.
- **Account**: owner, tax wrapper, currency, liquidity and positions; it is not an asset class.
- **Lot**: acquisition date, quantity and jurisdiction-specific basis. Units and total/per-unit basis must be explicit.
- **Policy**: a decision rule using only information available at the decision date. A policy cannot see future simulated returns.
- **Economic P&L** differs from recognized taxable income; a loss can be deferred, disallowed, or unusable this year.
- **Tax benefit**: the difference between matched household tax/cash-flow outcomes, not gross losses times a headline rate.
- **Distribution**: cash movement, which may differ from allocated taxable income, return or vesting.
- **Liquid wealth** excludes locked investments and unvested assets. Borrowing creates a liability and is not income.
- **Funding failure**: inability to meet the specified spending/tax obligations with permitted liquid resources, not simply negative terminal wealth.
- **Terminal wealth**: show continued-holding wealth and estimated spendable wealth under a stated exit separately. Show contingent taxes and lockups.
- **Conditional result**: valid only for its stated product/tax assumptions; never labelled verified manager performance.
- **Optimization result**: best among evaluated feasible policies unless a solver supplies a valid stronger certificate.

## Unknown private inputs

Actual balances, tax lots, birth dates, spending amounts, existing carryforwards, debt terms, compensation schedules and product contracts require private entry/confirmation. Public examples are independently synthetic. Cross-border identity, regional and eligibility fields remain unset until entered.
