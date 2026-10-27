"""An unsold worthless property still requires an actual native terminal transaction."""

from optimization_drilling_cases import inputs

from wealthlab.household.projection import project
from wealthlab.household.scenario import Scenario
from wealthlab.optimization.drilling_exits import completed


def test_unsold_zero_property_mark_does_not_become_a_completed_native_sale():
    household, _, _, _ = inputs()
    data = household.model_dump(mode="json")
    data["drilling_plan"]["observations"][0].update(
        residual_property_value="0", exit_requested=False, exit_gross_proceeds="0"
    )
    case = Scenario.model_validate(data)
    row = project(case)[-1]
    assert row["account_balances"]["drilling"] == 0
    assert completed(case, row) is False
