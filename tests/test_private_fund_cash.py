"""Actual wallet payments and independent conservation checks for conditional fund contracts."""

from household_sleeve_cases import change
from private_fund_cases import fund, request

from wealthlab.household.projection import project


def test_partial_distributions_exhaust_basis_only_on_actual_cash_and_full_exit():
    case = fund(
        federal_opening_basis="80000",
        requests=[request(30000), request(final=True, notice="2026-12-01", identity="exit")],
    )
    rows = project(case)
    first, last = rows[0], rows[-1]
    assert first["closing_cash"] == 40000
    assert first["account_balances"]["sleeve"] == 70000
    audit = last["sleeve_audit"]
    assert audit[0]["fund_basis"]["federal"] == 50000
    assert last["account_balances"]["sleeve"] == 0
    assert last["annual_tax"]["federal"]["agi"] == 20000
    assert last["net_wealth"] == 110000 - last["annual_tax"]["total_liability"]
    assert sum(r["tax_event_cash"] for r in rows) == 0


def test_internal_squeeze_cannot_take_household_cash_or_create_recourse_debt():
    def squeeze(data):
        sleeve = data["sleeve_plan"]["sleeves"][0]
        sleeve["observations"][0]["short_return"] = "4"

    rows = project(change(fund(), squeeze))
    assert rows[0]["sleeve_negative_equity"]
    assert rows[0]["sleeve_liability"] == 0
    assert rows[0]["closing_cash"] == 10000
    assert rows[0]["net_wealth"] == 10000
    assert rows[-1]["sleeve_audit"][0]["fund_nonrecourse_deficit"] == 20000
