# Bounded household policy search and separate validation

Issue18 starts with an editable finite search over the existing household engine. No second cash-flow, lot, tax or retirement engine is introduced. Python's Cartesian product enumerates explicit allowed choices; the existing pinned NumPy generator supplies one common training batch. The already integrated OWL reference remains a separate bounded retirement benchmark; it does not replace actual-lot/harvesting accounting. No new solver dependency is needed for an exhaustive finite menu.

## Choices, bounds and locks

A dimension contains named allowed choices and an optional lock to one choice. Choices replace native sale schedules, harvesting schedules, IRA withdrawal/conversion orders, taxable funding order, retirement dates or discretionary guardrails. Whole-schedule replacement distinguishes `null` (preserve) from `[]` (clear). A guardrail has an explicit change flag so clearing it is distinct from leaving it unchanged. Funding order is a permutation of existing permitted sources; it cannot create assets or alter sale permissions, fees or basis.

All choices within a dimension control the same fields. Different dimensions cannot overwrite each other's fields or the same person's retirement date. Each candidate starts from a fresh common household and is validated through the existing native adapters. Capital, income schedules, essential spending, tax facts, product terms and market expectations stay fixed across candidates. Retirement changes affect actual dated wages through the ordinary household rules. Guardrails can reduce only explicitly named discretionary expenses. Nothing is selected using knowledge of an individual path's future returns.

Execution assumptions are also compared across the baseline and every allowed choice, including locked alternatives. Sale commissions stay fixed for each account/security; harvest commission and replacement eligibility stay fixed for each account/source/replacement pair; explicit IRA penalty-exception assumptions stay fixed for each source account. Adding dates or changing amounts does not create permission to choose a lower commission or favorable tax exception. Distinct instruments or source accounts can retain independently supplied terms. This ordinary search profile does not optimize different exception purposes within one IRA; configure that factual context separately. Policy price placeholders are replaced by the existing live household marks at execution.

The product of allowed choices is the search bound. Explicit candidate and projection-month budgets are checked before generating paths; oversized searches fail instead of silently truncating. Every evaluated candidate and unsupported-profile reason is retained. Stable iteration breaks exact score ties by the first entered choice. The result claims only the best evaluated feasible candidate, never a global optimum beyond the configured menu.

## Safety before after-tax wealth

Starting targets remain 95% modeled joint funding/product success, through age100 of the younger member, with two years of cash reserves. All three are adjustable. The engine's exclusive horizon must cover the entire target-age year, ending no earlier than the next birthday. The short synthetic starter deliberately fails this default horizon constraint; positive wealth over two years cannot establish lifetime funding.

A candidate must meet the joint funding target and the separate reserve-success target, cover the horizon, have complete/resolved annual taxes, satisfy an enabled issuer-concentration limit, and complete its terminal exits on every evaluated path. Unknown issuer inventories do not satisfy an enabled limit. A user may explicitly disable that constraint with `null`; unknown coverage remains reported.

Within the feasible set, selection is lexicographic: larger joint funding-success fraction first, then median real after-tax exit wealth. Taxes paid, maximum shortfall, drawdown, discretionary reductions, cash and issuer coverage remain diagnostics, never a tax-minimization score. Downside wealth is the empirical fifth percentile using the nearest-rank definition, not an interpolated tail forecast.

Terminal ranking currently requires every noncash balance and residual taxable-lot quantity to be zero. An exit request, rounded zero account or attractive mark is insufficient. Actual supplied/native exits recognize their taxes and the existing wealth calculation deducts the tax position. Unreceived tax refunds remain receivables in wealth; they do not become spending cash. The selected household audit retains tax positions and actual cash. This is a strict completed-exit profile, not a generic estimated liquidation tax or inheritance forecast.

## Training and validation

Every candidate receives the same realized training batch and path indices. Validation requires a different seed with identical market assumptions and horizon; path counts may differ. Only the training winner runs on the held-out batch. Its selection is frozen before validation is generated. A failed or unsupported validation outcome is preserved; the algorithm never uses validation to choose a runner-up. Repeated manual tuning against a reused validation sample can still overfit and should not be interpreted as fresh independent evidence.

Both samples display the existing two-sided95% Wilson interval for funding/reserve fractions. Point-estimate target attainment does not assert statistical confidence or model correctness. This first search layer uses Monte Carlo samples. Existing deterministic, historical and named-stress workbenches remain available; a subsequent optimizer layer must apply these robustness comparisons to the frozen policy without treating stress frequencies as probabilities.

## Supported scope and remaining integration

This layer supports ordinary linked taxable lots, ordinary IRA schedules and compatible employment/benefit/Medicare inputs through their existing explicit rules. Product-specific exit certificates, workplace/HSA/education search integration, conditional blended allocations and cross-border interaction remain required follow-on work for issue18. Zero net product equity cannot prove that gross positions, contingent liabilities or future calls have closed. Unsupported product plans cannot enter the feasible ranking.

The Optimize workspace edits/imports the complete case, displays all candidates and constraints, and exports inputs, outcomes, the full selected calculation audit and the selected Household scenario. Invalid edits clear stale results. All data remain local; public examples are synthetic. The menu and funding-order controls are already concrete, while product allocation and robust cross-border optimization are not yet claimed complete.

Independent checks reconcile $300,000 opening capital minus $48,000 spending and $1 sale commission to $251,999 when the flat-market household retires immediately. Working one more year adds $60,000 gross wages less actual net taxes. A $10,000 IRA draw and a $10,000 conversion followed by a young Roth draw both preserve principal once and incur the explicitly modeled $1,000 additional tax. Bounds/locks, incomplete exits, horizon/issuer failures, sample separation, frozen failed validation and the native editable form have executable checks.
