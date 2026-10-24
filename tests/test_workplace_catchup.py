"""Shared future-rule limits retain actual calendar ages and high-earner Roth treatment."""

from decimal import Decimal

from wealthlab.household.projection import project
from wealthlab.household.scenario import Scenario
from wealthlab.retirement.workplace_example import synthetic


def test_future_age_sixty_high_earner_catchup_is_roth_and_shared():
    data = synthetic().model_dump(mode="json")
    data.update(start="2030-01-01", end="2031-01-01")
    for person in data["members"]:
        person["retirement_date"] = "2040-01-01"
    data["members"][0]["birth_date"] = "1970-06-01"
    income = data["incomes"][0]
    income.update(start="2030-01-01", end="2031-01-01", monthly_amount="50000")
    year = data["workplace_plan"]["years"][0]
    year["year"] = 2030
    year["contributors"][0].update(
        birth_date="1970-06-01",
        workplace_compensation="600000",
        prior_employer_wages="160000",
        catchup_permitted=True,
    )
    orders = [data["workplace_plan"]["orders"][0], data["workplace_plan"]["orders"][-1]]
    orders[0].update(date="2030-01-01", amount="40000")
    orders[1].update(date="2030-02-01", amount="20000")
    data["workplace_plan"]["orders"] = orders
    # Regenerate dated tax filing context instead of retaining 2026 ages.
    from wealthlab.tax.projection_example import template

    scenario = Scenario.model_validate(data)
    scenario = scenario.model_copy(update=dict(tax_plan=template(scenario)))
    row = project(scenario)[-1]
    assert row["account_balances"]["work_pretax"] == Decimal(24500)
    assert row["account_balances"]["work_roth"] == Decimal(11250)
    assert row["workplace_audit"][0]["blocked_by_limit"] == Decimal(15500)
