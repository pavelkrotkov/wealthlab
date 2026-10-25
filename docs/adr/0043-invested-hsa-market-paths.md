# 0043. Actual invested-HSA market paths

Status: accepted, bounded issues #6/#8 increment. This extends the actual household HSA adapter, not a complete retirement optimizer.

## Decision

`HouseholdBinding.hsa_securities` binds each ordinary invested-HSA security exactly once to an existing market factor and independently assumed NJ cash-income character. Explicit replacement confirmation is required. The path copy replaces entered prices, distributions and security locks; source inputs remain immutable. Supplied lots, jurisdictional basis, contribution/recipient schedules, fixed cash targets, custodian fee terms and original lot liquidity dates persist. Manual fixed-price HSA executions and reinvested-total-return inputs are rejected by this price-plus-cash profile.

All four existing generators work: deterministic assumptions, supplied historical replay, correlated Monte Carlo and named stress. Closing share prices compound only the supplied price return and become observable on the month's last day. The supplied cash yield is credited on the first day, using previous closing prices and actual opening shares. Generated entitlement/payment/recognition precede that day's recipient orders. This explicit monthly convention is not an issuer dividend calendar or a claim of actual historical distributions. Yield remains inside the HSA; it never enters ordinary household cash or federal investment income. NJ recognition follows the independently selected dividend/interest/exempt character. Actual sales continue using separate NJ basis.

Scenario factor locks prevent share sales throughout their declared months without destroying marked positions. Custodian assessment prices use the most recent observable path mark; cash charges, commissions and fee arrears remain in their existing actual books. Qualified medical payments and nonqualified recipient orders continue using actual eligible funding, provider/cash fallback and explicit tax treatment. An account can have positive wealth while failing to pay its bill.

Security and factor exposure include actual remaining HSA shares. Display keys use an HSA prefix to keep their identity separate from taxable-book IDs. The bound HSA account is no longer silently omitted from factor coverage; unrelated unmeasured accounts retain their diagnostics. Cash and dividend receivables remain account assets, not equity-factor positions or automatically spendable household reserves.

## UI and checks

Markets / Household funding / **Invested HSA** uses the original synthetic medical case and exports the same actual ledger as Household, including remaining lots, distributions, provider payments, state income and fees. It also exposes paired household/binding policies on identical realized batches and indices.

The independent flat-price/zero-yield check starts with $11,100, pays $6,000 care, $2 commission and $50 custody fees, leaving $5,048. A $4,952 gross sale at $100 disposes of 49.52 shares with $2,971.20 NJ basis; $4,950 net proceeds therefore realize $1,978.80 NJ gain despite flat market prices. Twelve monthly $100 interest receipts leave $6,248 and change shares sold/state gain, while federal investment income and household tax-event cash remain zero.

Other checks cover all four modes, immutable source inputs, a December 15 provider sale using the November rather than December closing quote, illiquidity with positive wealth and unpaid care, binding/return/trade guards, existing taxable/wrapper/medical path regressions and the real UI. Results concern the supplied horizon; the one-year synthetic case cannot establish funding safety through age 100.
