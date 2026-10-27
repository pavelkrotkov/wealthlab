"""Dated forecast views retain native paired carry semantics without changing actual returns."""

from wealthlab.portfolio.household_budget_inputs import validate_order, validate_source
from wealthlab.portfolio.household_budget_rules import validate as validate_rules
from wealthlab.portfolio.tax_reporting import validate_tax_cases


def validation_case(plan, scenario):
    policies = [policy for policy in plan.case.sale_policies if policy.mode == "tax_budget"]
    if not policies:
        return plan.case
    forecasts = plan.tax_budget_forecasts
    if not forecasts:
        raise ValueError(
            "Household tax-budget decisions need an explicit dated annual-forecast adapter."
        )
    validate_order(forecasts, plan.case.end)
    actual = {case.policy.year: case for case in scenario.tax_plan.cases}
    for forecast in forecasts:
        validate_source(forecast)
        view = plan.case.model_copy(update={"lot_tax_cases": forecast.cases})
        validate_tax_cases(view)
        validate_rules(forecast.cases, actual)
    for policy in policies:
        select(plan, policy.date)
    return plan.case.model_copy(update={"lot_tax_cases": forecasts[0].cases})


def select(plan, when):
    observed = [forecast for forecast in plan.tax_budget_forecasts if forecast.available_on <= when]
    if not observed:
        raise ValueError("No annual budget forecast is available by this policy's decision date.")
    return observed[-1]
