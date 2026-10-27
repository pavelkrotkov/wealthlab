"""Original one-year forecast-error fixture: an unreceived bonus cannot become household income."""

from wealthlab.household.scenario import Scenario
from wealthlab.portfolio.budget_household_example import enable
from wealthlab.portfolio.household_example import lot
from wealthlab.portfolio.household_example import synthetic as original


def synthetic():
    data = original().model_dump(mode="json")
    data.update(name="Synthetic conditional household tax-budget forecast", end="2027-01-01")
    data.update(incomes=[], expenses=[], debts=[], contributions=[])
    data["accounts"][1]["balance"] = "10000"
    data["lot_plan"]["case"].update(end="2026-12-31", lots=[lot("original", "100", "5000", "6000")])
    data["lot_plan"]["monthly_marks"] = data["lot_plan"]["monthly_marks"][:12]
    data["lot_plan"]["case"]["closing_prices"] = dict(stock="100")
    data["lot_plan"]["funding_sources"][0]["commission"] = "0"
    data["tax_plan"]["cases"] = data["tax_plan"]["cases"][:1]
    data["tax_plan"]["income_rules"] = []
    data["tax_plan"]["funding_sources"] = []
    result = enable(Scenario.model_validate(data))
    policies = result.lot_plan.case.sale_policies[:1]
    book = result.lot_plan.case.model_copy(update={"sale_policies": policies})
    return result.model_copy(update={"lot_plan": result.lot_plan.model_copy(update={"case": book})})


def two_year():
    data = synthetic().model_dump(mode="json")
    original_data = original().model_dump(mode="json")
    data["end"] = "2028-01-01"
    data["tax_plan"]["cases"] = original_data["tax_plan"]["cases"]
    data["lot_plan"]["case"]["end"] = "2027-12-31"
    data["lot_plan"]["monthly_marks"] = [
        dict(mark, prices=dict(stock="100")) for mark in original_data["lot_plan"]["monthly_marks"]
    ]
    return enable(Scenario.model_validate(data))
