"""A supported maximum-length account ID must remain executable through an actual cash exit."""

from household_sleeve_cases import change
from private_fund_cases import fund, request

from wealthlab.household.projection import project


def test_maximum_length_account_id_cannot_overflow_generated_exit_allocation_ids():
    identity = "f" * 80

    def configure(data):
        data["accounts"][1]["id"] = identity
        data["sleeve_plan"]["sleeves"][0]["account_id"] = identity

    case = change(fund(federal_opening_basis="80000", requests=[request(final=True)]), configure)
    rows = project(case)
    assert rows[-1]["annual_tax"]["federal"]["agi"] == 20000
    assert rows[-1]["account_balances"][identity] == 0
    assert rows[-1]["sleeve_audit"][-1]["fund_complete_liquidation"]
