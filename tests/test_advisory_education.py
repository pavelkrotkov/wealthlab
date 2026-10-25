"""Native 529 deposits respect the same fee reservation without creating a second cash balance."""

from tests.advisory_cases import with_fee
from wealthlab.household.projection import project
from wealthlab.household.scenario import Scenario
from wealthlab.retirement.education_household_example import synthetic


def test_optional_529_deposit_retains_outer_fee_cash_without_changing_contribution_basis_twice():
    data = synthetic().model_dump(mode="json")
    data.update(incomes=[], expenses=[], hsa_plan=None, ira_plan=None)
    data["tax_plan"]["income_rules"] = []
    data["accounts"] = [a for a in data["accounts"] if a["id"] in {"cash", "college"}]
    data["accounts"][0]["balance"] = "1000"
    plan = data["education_plan"]
    plan["tuition"], plan["returns"] = [], []
    plan["contributions"] = [
        dict(
            id="optional_529",
            provenance="illustration",
            date="2026-01-15",
            destination="college",
            amount="1000",
        )
    ]
    rows = project(with_fee(Scenario.model_validate(data), account="cash", rate="0", fixed="100"))
    assert rows[0]["education_deposits"] == 900
    assert rows[0]["education_unfilled_deposits"] == 100
    assert rows[0]["advisory_fees_paid"] == 100
    assert rows[0]["closing_cash"] == 0
    assert rows[0]["account_balances"]["college"] == rows[0]["net_wealth"] == 30900
