"""Gross wages must have one owner and one tax mapping before payroll elections.

Annual opening wages or manual wage events would bypass the current-payroll
capacity test. This complete-year bridge therefore requires dated wage
streams instead; the pre-existing employment adapter can generate them.
"""


def validate_wages(scenario):
    plan = scenario.tax_plan
    if any(wage_facts(c.federal_income, c.nj_income) for c in plan.cases):
        raise ValueError(
            "Employee bridge uses generated wages, not manual annual wage/deferral facts."
        )
    if any(wage_facts(e.federal, e.new_jersey) for e in plan.events):
        raise ValueError("Remove manual wage/deferral events when generating employee elections.")
    validate_rules(scenario)


def validate_rules(scenario):
    plan = scenario.tax_plan
    members = [m.id for m in scenario.members]
    incomes = {i.id: i for i in scenario.incomes}
    for r in plan.income_rules:
        if r.federal not in {"wages_primary", "wages_spouse"}:
            continue
        owner = members[0] if r.federal == "wages_primary" else members[-1]
        validate_rule(r, incomes[r.income_id], owner)


def validate_rule(rule, income, owner):
    if income.owner != owner or rule.new_jersey != "wages" or income.currency != "USD":
        raise ValueError("Map each owner's gross USD wages consistently to federal and NJ wages.")


def wage_facts(federal, nj):
    return any(
        (
            federal.wages_primary,
            federal.wages_spouse,
            federal.deferrals_primary,
            federal.deferrals_spouse,
            nj.wages,
        )
    )
