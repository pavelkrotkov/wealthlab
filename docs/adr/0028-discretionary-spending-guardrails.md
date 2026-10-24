# ADR 0028: Observed-wealth discretionary spending guardrail

Status: an optional policy in [actual household market execution](0027-household-market-execution.md), part of open market/optimization work. Fixed spending remains the default. This is an adjustable scenario rule, not a recommended retirement withdrawal formula.

## Rule and information timing

The policy names existing discretionary expense IDs, a monthly/quarterly/annual review interval, a real-net-wealth drawdown trigger, a smaller restoration threshold, a cut fraction and a minimum spending fraction. Duplicate IDs, unknown/essential budgets, invalid hysteresis and floor-violating cuts block. Positive opening net wealth and confirmation that net wealth includes spending/cash-flow effects are required.

At each scheduled review after the first month, compare the latest observed real net wealth with its observed high-water mark. Crossing the decline trigger activates one fixed reduction. Recovery inside the smaller restoration threshold removes it. Between thresholds, retain the current state. The policy never sees the current month's later prices or future simulated returns. It does not compound cuts or rewrite earlier spending.

Selected expenses first receive their explicitly configured prior-CPI adjustment, then the guardrail scales their otherwise current schedule. Restoration uses the fresh uncut schedule. Essential, healthcare, education and other unselected budgets retain their inputs. Review dates and the prior observed decline, active state and current USD spending reduction are preserved in every row.

## Funding is conditional on the actual requested lifestyle

The model reports planned discretionary spending reductions separately from unmet bills. A guardrail can improve wealth or funding by asking the household to spend less; that is an explicit lifestyle cost, not evidence that the original uncut spending was funded. Paired policy output reports the difference in reductions alongside wealth and shortfalls on identical paths. Optimizers must retain this cost/objective distinction.

Net wealth includes taxes, spending and external contributions; a decline can therefore trigger without a market loss. It is deliberately labeled a wealth-based rule. Cash-reserve constraints, return-only rules, repeated multistep cuts and optimized guardrail parameters are separate requested policy work, not hidden features of this rule.

## Executed checks

A matched two-year case starts with $101,000 and two $1,000 monthly budgets, essential and discretionary. A first-month 50% price loss cannot reduce that first bill. Monthly reviews cut only discretionary spending to $800 for the following 23 months: $4,600 reduced spending preserves exactly $4,600 terminal real wealth in the flat subsequent path. Cuts do not compound. A subsequent observed recovery restores the third month's original $1,000; annual reviews cannot act before month 13. Contract/scope guards and the real Markets UI check the adjustable synthetic example.

The synthetic starter splits an existing $5,000 spending stream into $3,000 essential and $2,000 discretionary, preserving its initial total. Its monthly review, 20% trigger, 10% restoration threshold and 20% cut/80% floor are visible editable assumptions. No tax rule or third-party dependency is added.
