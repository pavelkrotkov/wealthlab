"""Actual option capital and SSA work-test claims coexist without duplicating either cash book."""

from tests.social_work_household_cases import payload
from wealthlab.household.projection import project
from wealthlab.household.scenario import Scenario
from wealthlab.products.option_household_example import synthetic


def test_option_assignment_preserves_ssa_claims_and_adds_actual_after_tax_proceeds_once():
    data = payload()
    data["end"] = "2027-01-01"
    data["social_security"]["end_year"] = 2027
    data["social_work_plan"]["years"] = data["social_work_plan"]["years"][:1]
    data["tax_plan"]["cases"] = data["tax_plan"]["cases"][:1]
    data["accounts"][0]["balance"] = "100000"
    baseline = project(Scenario.model_validate(data))
    options = synthetic().model_dump(mode="json")
    data["accounts"].append(options["accounts"][1])
    data["option_plan"] = options["option_plan"]
    actual = project(Scenario.model_validate(data))
    base, combined = baseline[-1], actual[-1]
    assert (
        combined["social_security_government_receivable"]
        == base["social_security_government_receivable"]
    )
    assert combined["option_shares"] == 0
    tax_difference = (
        combined["annual_tax"]["total_liability"] - base["annual_tax"]["total_liability"]
    )
    assert combined["net_wealth"] - base["net_wealth"] == 11500 - tax_difference
    assert combined["closing_cash"] - base["closing_cash"] == 11500 - tax_difference
