"""Physical liquidation and completion of supplied recognition schedules remain separate."""

from exchange_allocation_cases import allocated

from wealthlab.household.projection import project
from wealthlab.household.scenario import Scenario


def test_pending_future_supplied_loss_prevents_a_complete_modeled_exit_claim():
    data = allocated(1000).model_dump(mode="json")
    item = data["exchange_fund_plan"]["observations"][0]["allocation"]
    item["federal"]["long_term"] = "-1000"
    item["federal_loss"].update(
        treatment="deferred", release_on="2027-01-15", eligibility_after_limits_assumed=True
    )
    final = project(Scenario.model_validate(data))[-1]
    audit = final["exchange_fund_audit"]
    assert final["exchange_positions_closed"] is True
    assert audit["exit_status"]["unrecognized_future_events"] == 1
    assert audit["exit_status"]["modeled_exit_complete"] is False
    assert final["annual_tax"]["federal"]["agi"] == 80000
