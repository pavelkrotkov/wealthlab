"""Derive actual current earned W2 before payroll elections; forecasts remain supplied inputs."""

from decimal import Decimal

from wealthlab.household.calendar import months
from wealthlab.household.flows import earning_items

ZERO = Decimal(0)


def wage_rules(scenario):
    owners = [person.id for person in scenario.members]
    fields = dict(zip(("wages_primary", "wages_spouse"), owners, strict=False))
    incomes = {income.id: income for income in scenario.incomes}
    result = {}
    for rule in scenario.tax_plan.income_rules:
        if rule.federal not in fields:
            continue
        income = incomes[rule.income_id]
        owner = fields[rule.federal]
        if income.currency != "USD":
            raise ValueError("Current earned W2 streams require USD in this profile.")
        result[income.id] = owner
    return result


def realized(scenario):
    rules = wage_rules(scenario)
    wages = {
        (year, person.id): [ZERO] * 12
        for year in range(scenario.start.year, scenario.end.year)
        for person in scenario.members
    }
    for start, end in months(scenario.start, scenario.end):
        for identifier, value in earning_items(scenario, start, end).items():
            if identifier in rules:
                wages[(start.year, rules[identifier])][start.month - 1] += value
    return [
        row.model_copy(
            update=dict(actual_monthly_wages=wages.get((row.year, row.member), [ZERO] * 12))
        )
        for row in scenario.social_work_plan.years
    ]
