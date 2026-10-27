"""Original nominal-schedule forecasts include an explicitly assumed unreceived bonus."""

from datetime import timedelta

from wealthlab.household import flows
from wealthlab.household.calendar import months
from wealthlab.household.scenario import Scenario
from wealthlab.tax import recognition
from wealthlab.tax.annual import AnnualCase, Payments


def enable(scenario):
    data = scenario.model_dump(mode="json")
    data["lot_plan"]["case"]["sale_policies"] = [
        policy(end - timedelta(days=1), scenario.lot_plan.opening_prices)
        for start, end in months(scenario.start, scenario.end)
        if start.month in (1, 2)
    ]
    data["lot_plan"]["tax_budget_forecasts"] = [
        dict(
            id="illustrative_full_annual_forecast",
            provenance="illustration",
            source_reference="Original scheduled income plus hypothetical unreceived annual bonus",
            source_date=scenario.start.isoformat(),
            available_on=scenario.start.isoformat(),
            cases=[annual.model_dump(mode="json") for annual in forecasts(scenario)],
            known_non_lot_facts_and_remaining_income_confirmed=True,
            excludes_all_modeled_lot_events_confirmed=True,
            fixed_forecast_deductions_confirmed=True,
        )
    ]
    return Scenario.model_validate(data)


def policy(when, prices):
    return dict(
        id=f"budget_{when.year}_{when.month}",
        provenance="illustration",
        date=when.isoformat(),
        account_id="brokerage",
        security_id="stock",
        mode="tax_budget",
        tax_budget="500",
        budget_grid_points=8,
        prices=prices,
        commission="0",
        selection="hifo",
    )


def forecasts(scenario):
    # This starter uses only entered nominal schedules, never a realized market
    # path. The extra bonus is a forecast assumption and has no income event.
    cases = {annual.policy.year: annual for annual in scenario.tax_plan.cases}
    for start, end in months(scenario.start, scenario.end):
        cases[start.year] = recognition.scheduled(
            cases[start.year],
            flows.earning_items(scenario, start, end),
            scenario.tax_plan.income_rules,
        )
    result = []
    for annual in cases.values():
        data = annual.model_dump()
        data["payments"] = Payments().model_dump()
        data["federal_income"]["wages_primary"] += 200000
        data["nj_income"]["wages"] += 200000
        result.append(AnnualCase.model_validate(data))
    return result
