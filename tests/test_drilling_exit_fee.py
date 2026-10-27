"""Transaction costs reduce net liquidation proceeds without becoming operating deductions."""

from drilling_cases import change, short

from wealthlab.household.projection import project


def test_exit_fee_reduces_actual_cash_and_gain_once():
    case = change(short(), lambda d: d["drilling_plan"]["observations"][0].update(exit_fee="5000"))
    row = project(case)[0]
    assert (row["drilling_exit_cash"], row["drilling_federal_exit_gain"]) == (35000, 15000)
    assert (row["drilling_net_operating_income"], row["annual_tax"]["federal"]["agi"]) == (
        -10000,
        -65000,
    )
    assert row["drilling_paid_costs"]["exit_cost"] == 5000
