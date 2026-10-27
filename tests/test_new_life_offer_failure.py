"""A selected new issue still needs an actual funded premium to obtain any protection."""

from new_life_offer_cases import inputs

from wealthlab.household.projection import project
from wealthlab.household.scenario import Scenario
from wealthlab.optimization.new_life_offers import apply


def test_unfunded_first_premium_creates_no_asset_basis_coverage_or_later_receipt():
    household, offers = inputs()
    data = household.model_dump(mode="json")
    data["accounts"][0]["balance"] = "500"
    data["expenses"][0]["monthly_amount"] = "0"
    apply(data, offers, [offers[0].id])
    rows = project(Scenario.model_validate(data))
    assert [r["closing_cash"] for r in rows] == [500, 500, 500]
    assert [r["life_net_death_benefit"] for r in rows] == [0, 0, 0]
    assert rows[0]["life_payment_unfunded"] == 1000
    assert rows[-1]["life_policy_audit"]["executed"][0]["federal_basis_after"] == 0
