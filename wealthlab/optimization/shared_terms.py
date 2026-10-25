"""Decision schedules cannot select their own favorable fee or tax-eligibility assumption.

The baseline and every allowed choice share cost/eligibility terms for the
same execution source, including locked alternatives. Dates, amounts, sale
modes and selection order remain decisions. Live household marks replace
policy price placeholders at execution; prices are not searched forecasts.
"""


def validate(case):
    lots, ira = case.household.lot_plan, case.household.ira_plan
    sales = lots.case.sale_policies if lots is not None else []
    harvests = lots.case.harvest_policies if lots is not None else []
    orders = ira.orders if ira is not None else []
    same(
        schedules(case, "sale_policies", sales),
        ("account_id", "security_id"),
        ("commission",),
        "sale commission",
    )
    same(
        schedules(case, "harvest_policies", harvests),
        ("account_id", "security_id", "replacement_id"),
        ("commission_per_trade", "replacement_eligible"),
        "harvest terms",
    )
    same(
        schedules(case, "ira_orders", orders),
        ("source",),
        ("early_penalty_exception",),
        "IRA penalty exception",
    )


def schedules(case, name, baseline):
    yield from baseline
    for dimension in case.dimensions:
        for choice in dimension.choices:
            yield from getattr(choice, name) or []


def same(rows, identifiers, assumptions, label):
    observed = {}
    for row in rows:
        key = tuple(getattr(row, field) for field in identifiers)
        terms = tuple(getattr(row, field) for field in assumptions)
        if key in observed and observed[key] != terms:
            raise ValueError(
                f"Keep shared {label} assumptions fixed across the baseline and all choices."
            )
        observed[key] = terms
