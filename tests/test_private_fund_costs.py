"""Actual cash exit costs reduce ending wealth once, independently of tax recognition."""

from decimal import Decimal

from household_sleeve_cases import change
from private_fund_cases import fund, request

from wealthlab.household.projection import project


def test_exit_costs_and_gates_conserve_economics_without_duplicate_cash():
    def costs(data):
        data["sleeve_plan"]["sleeves"][0]["case"]["exit_cost"] = ".01"

    rows = project(change(fund(requests=[request(final=True)]), costs))
    assert rows[0]["closing_cash"] == Decimal("108400")
    assert rows[0]["account_balances"]["sleeve"] == 0
    assert rows[-1]["sleeve_audit"][0]["exit_cost"] == 1600
    assert rows[-1]["net_wealth"] == 108400
