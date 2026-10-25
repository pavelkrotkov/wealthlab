"""A December earned-wage surprise creates later debt without changing earlier household cash."""

from social_work_household_cases import case, payload

from wealthlab.household.projection import project
from wealthlab.household.scenario import Scenario


def test_future_realized_wage_change_keeps_prior_household_rows_identical():
    original = project(case())
    raw = payload()
    wage = dict(
        raw["incomes"][0],
        id="surprise-pay",
        start="2026-12-01",
        end="2027-01-01",
        monthly_amount=100000,
    )
    raw["incomes"].append(wage)
    raw["tax_plan"]["income_rules"].append(
        dict(income_id="surprise-pay", federal="wages_primary", new_jersey="wages")
    )
    changed = project(Scenario.model_validate(raw))
    assert changed[:11] == original[:11]
    assert changed[11]["social_security_government_overpayment_debt"] == 2810
    assert changed[16]["social_security_recovered_overpayment"] == 562
    assert changed[16]["social_security_government_overpayment_debt"] == 2810
