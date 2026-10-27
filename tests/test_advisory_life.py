"""Sourced net cash and surrender bases come from the executed policy, without duplicate loans."""

from decimal import Decimal

import pytest

from tests.advisory_cases import change, with_fee
from wealthlab.household.projection import project
from wealthlab.household.scenario import Scenario
from wealthlab.products.life_household_example import synthetic


@pytest.mark.parametrize(
    "basis, expected", [("life_net_cash_value", 120), ("life_net_surrender_value", 109)]
)
def test_native_life_values_and_outer_cash_fee_preserve_policy_basis_and_embedded_costs(
    basis, expected
):
    data = synthetic().model_dump(mode="json")
    data["life_plan"]["holdings"][0]["contract"]["values"][0]["gross_cash_value"] = "12000"
    case = Scenario.model_validate(data)
    baseline = project(case)
    fee_case = with_fee(case, account="life_policy", rate=".12")

    def basis_choice(plan):
        plan["schedules"][0]["covered"][0]["value_basis"] = basis

    rows = project(change(fee_case, basis_choice))
    assert rows[0]["advisory_fees_paid"] == expected
    assert rows[-1]["net_wealth"] == baseline[-1]["net_wealth"] - expected
    assert (
        rows[0]["life_policy_values"][0]["federal_basis"]
        == baseline[0]["life_policy_values"][0]["federal_basis"]
    )
    assert rows[-1]["life_policy_values"][0]["loan"] == Decimal(500)
