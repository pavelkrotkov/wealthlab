"""Actual contributions and costs conserve capital through a complete taxable cash exit."""

from drilling_cases import change, short

from wealthlab.household.projection import project
from wealthlab.products.drilling_compare import compare


def test_flat_liquid_reference_returns_capital_once_while_actual_well_costs_reduce_wealth():
    case = short()
    original = case.model_dump_json()
    result = compare(case)
    drilling = result["rows"]["drilling"][-1]
    liquid = result["rows"]["liquid_reference"][-1]
    assert (drilling["net_wealth"], liquid["net_wealth"]) == (140000, 200000)
    assert (drilling["drilling_exit_cash"], liquid["drilling_exit_cash"]) == (40000, 100000)
    assert result["outcomes"]["liquid_reference"]["distributions"] == 100000
    assert drilling["account_balances"]["drilling"] == 0
    assert sum(r["tax_event_cash"] for r in result["rows"]["drilling"]) == 0
    assert case.model_dump_json() == original


def test_production_royalties_paid_operating_costs_and_terminal_cash_conserve_value():
    def configure(data):
        data["drilling_plan"]["observations"][1]["royalty_fraction"] = ".25"

    rows = project(change(short(2), configure))
    last = rows[-1]
    assert last["drilling_production_receipts"] == 1000
    assert last["drilling_royalties"] == 250
    assert last["drilling_net_operating_income"] == 550
    assert last["drilling_exit_cash"] == 40550
    assert last["net_wealth"] == 140550
