"""A logical subaccount is not a separate designated Roth tax contract."""

from wealthlab.household.projection import project
from wealthlab.household.scenario import Scenario
from wealthlab.retirement.workplace_roth_example import synthetic


def test_a_whole_subaccount_draw_uses_the_complete_plan_contract_denominator():
    data = synthetic().model_dump(mode="json")
    data["accounts"][1]["balance"] = 5000
    data["accounts"].append(dict(data["accounts"][1], id="roth_second"))
    data["workplace_plan"]["products"]["roth_second"] = "roth_401k"
    data["workplace_plan"]["roth_cash_withdrawals"]["contracts"]["ordinary"]["sources"].append(
        "roth_second"
    )
    rows = project(Scenario.model_validate(data))
    row = rows[-1]["workplace_roth_audit"][0]
    assert row["contract_value_before"] == 10000
    assert row["federal_basis_recovered"] == 4700
    assert row["federal_taxable"] == 300
    assert rows[-1]["account_balances"]["work_roth"] == 0
    assert rows[-1]["account_balances"]["roth_second"] == 5000
