"""Rebind only explicit monthly USD wages using native employment/calendar accruals.

Opening income and all source claims remain fixed. Native country-specific
helpers retain person, receipt date and independent currency translation.
"""

from datetime import timedelta
from decimal import Decimal

from wealthlab.employment.wages import split
from wealthlab.household.calendar import amount, months
from wealthlab.household.scenario import Scenario
from wealthlab.tax.country_wage_sources import update_credit
from wealthlab.tax.pr_wage_sources import update_pr
from wealthlab.tax.spain_execution_facts import SpainExecution
from wealthlab.tax.spain_wage_sources import update_spain


def validate(scenario, context):
    supplied = [(r.income_id, r.date) for r in context.wage_sources]
    sources = [(r.source_id, r.date.year) for r in context.wage_sources]
    if len(supplied) != len(set(supplied)) or len(sources) != len(set(sources)):
        raise ValueError("Bind each monthly income and country source exactly once.")
    if set(supplied) != expected_sources(scenario):
        raise ValueError("Every projected income needs its explicit monthly country wage binding.")
    if supplied and any((scenario.workplace_plan, scenario.hsa_plan)):
        raise ValueError(
            "Country wage bindings do not infer workplace/HSA taxable wage adjustments."
        )
    prepare(scenario, context)


def prepare(scenario, context):
    data = scenario.model_dump(mode="json")
    spain = context.spain.model_dump(mode="json") if context.spain is not None else None
    for binding in context.wage_sources:
        income = next(i for i in scenario.incomes if i.id == binding.income_id)
        value = wage_amount(scenario, income, binding.date)
        update_credit(data, binding, income.owner, value)
        update_pr(data, binding, income.owner, value)
        update_spain(spain, binding, income.owner, value)
    return Scenario.model_validate(data), SpainExecution.model_validate(spain) if spain else None


def wage_amount(scenario, income, when):
    rule = next(r for r in scenario.tax_plan.income_rules if r.income_id == income.id)
    members = {m.id: m for m in scenario.members}
    if income.currency != "USD" or rule.federal not in {"wages_primary", "wages_spouse"}:
        raise ValueError("Country wage bindings require an actual USD W2 income rule.")
    start, end = wage_period(scenario, when)
    cutoff = min(end, members[income.owner].retirement_date) if income.stop_at_retirement else end
    pieces = wage_pieces(scenario, income)
    return sum((amount(piece, start, cutoff, scenario) for piece in pieces), Decimal(0))


def expected_sources(scenario):
    return {
        (income.id, end - timedelta(days=1))
        for income in scenario.incomes
        for start, end in months(scenario.start, scenario.end)
        if income.start < end and income.end > start
    }


def wage_period(scenario, when):
    periods = {
        end - timedelta(days=1): (start, end) for start, end in months(scenario.start, scenario.end)
    }
    if when not in periods:
        raise ValueError("A country wage source must retain its actual projected month-end date.")
    return periods[when]


def wage_pieces(scenario, income):
    paths = scenario.employment_plan.paths if scenario.employment_plan else []
    path = next((p for p in paths if income.id in p.income_ids), None)
    index = list(scenario.incomes).index(income)
    pieces = split(income, path, index) if path is not None else [income]
    return pieces
