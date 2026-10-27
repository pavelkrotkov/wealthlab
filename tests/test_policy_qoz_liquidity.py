"""An unpaid stock settlement cannot win after-tax exit ranking even with its full marked claim."""

from optimization_qoz_cases import case, changed

from wealthlab.optimization.search import search


def test_pending_fund_cash_fails_exit_while_the_same_source_and_immediate_reference_can_exit():
    def edit(data):
        data["household"]["qoz_plan"]["settlement_months"] = 2
        for offered in data["qoz_offers"]:
            if offered["plan"] and offered["plan"]["mode"] == "fund":
                offered["plan"]["settlement_months"] = 2

    result = search(changed(case(), edit))
    candidates = result["candidates"]
    assert [c["constraints"]["completed_after_tax_exit"] for c in candidates] == [
        True,
        False,
        False,
        True,
    ]
    assert candidates[1]["median_real_after_tax_exit_wealth"] is None
    assert candidates[1]["median_marked_real_wealth"] == 103753
    assert result["held_out"]["assessment"]["median_real_after_tax_exit_wealth"] == 103753
