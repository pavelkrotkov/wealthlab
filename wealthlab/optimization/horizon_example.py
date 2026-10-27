"""A complete synthetic cash/stock retirement horizon, with every future rule explicit.

This generates a new educational case only. It does not extend private inputs or
manufacture future contract values. Frozen2025 annual tax assumptions and source
price placeholders are disclosed; actual paths replace all monthly stock marks.
"""

from datetime import date, timedelta

from wealthlab.household.calendar import months
from wealthlab.household.scenario import Scenario
from wealthlab.markets.household_report import target_end
from wealthlab.optimization.example import synthetic as short_example
from wealthlab.optimization.inputs import PolicySearch
from wealthlab.tax.projection_example import template


def synthetic(cash=2000000, wages=5000, spending=2000, target_age=100):
    data = short_example().model_dump(mode="json")
    household = data["household"]
    household["target_age"] = data["targets"]["target_age"] = target_age
    required = target_end(Scenario.model_validate(household))
    end = complete_year(required)
    household.update(
        name="Synthetic full-horizon cash and stock retirement search", end=end.isoformat()
    )
    household["accounts"][0]["balance"] = str(cash)
    household["tax_plan"] = None
    for income in household["incomes"]:
        income.update(end=end.isoformat(), monthly_amount=str(wages))
    for expense in household["expenses"]:
        expense.update(end=end.isoformat(), monthly_amount=str(spending))
    extend_lots(household, end)
    household["tax_plan"] = template(Scenario.model_validate(household)).model_dump(mode="json")
    for name in ("training", "validation"):
        data[name]["end"] = end.isoformat()
    data["binding"]["inflation_expenses"] = ["living"]
    for choice, year in zip(data["dimensions"][0]["choices"], (2036, 2041), strict=True):
        choice["retirement_dates"]["person_a"] = f"{year}-01-01"
    return PolicySearch.model_validate(data)


def complete_year(required):
    return required if (required.month, required.day) == (1, 1) else date(required.year + 1, 1, 1)


def extend_lots(household, end):
    linked = household["lot_plan"]
    prices = linked["opening_prices"]
    last = end - timedelta(days=1)
    linked["case"].update(end=last.isoformat(), closing_prices=dict(prices))
    linked["case"]["sale_policies"][0]["date"] = last.isoformat()
    linked["monthly_marks"] = [
        dict(date=(following - timedelta(days=1)).isoformat(), prices=dict(prices))
        for _, following in months(date.fromisoformat(household["start"]), end)
    ]
