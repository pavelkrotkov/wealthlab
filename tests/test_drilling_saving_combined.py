"""Required product capital precedes optional saving; actual shares preserve household equity."""

from drilling_saving_cases import blended

from wealthlab.household.projection import project


def test_optional_saving_cannot_steal_the_required_drilling_capital_call():
    rows = project(blended())
    first, last = rows[0], rows[-1]
    assert (first["drilling_call_funded"], first["drilling_call_owed"]) == (100000, 0)
    assert (first["saving_spent"], first["saving_unfilled"]) == (0, 500)
    assert first["funding_failure"] is False
    assert sum(row["saving_spent"] for row in rows) == 1000
    assert last["account_balances"]["brokerage"] == 1000
    assert last["net_wealth"] + last["annual_tax"]["total_liability"] == 41600


def test_saving_buys_real_lots_and_keeps_both_final_audits():
    last = project(blended())[-1]
    lots = last["lot_audit"]["lots"]
    assert len(lots) == 2
    assert sum(float(lot["federal_basis"]) for lot in lots) == 1000
    assert sum(row["spent"] for row in last["saving_audit"]) == 1000
    assert ("drilling_audit" in last, "saving_audit" in last) == (True, True)
