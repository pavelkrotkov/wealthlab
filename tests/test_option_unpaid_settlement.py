"""Unpaid option settlement must survive a later long-only Book sale and remain owed."""

from tests.option_cases import one_leg, parse
from wealthlab.products.option_engine import run


def test_independent_index_obligation_survives_actual_stock_unwind_without_becoming_a_fee():
    data = one_leg(side="short", unwind=True)
    data["legs"][0]["underlying"] = "INDEX"
    data["holdings"]["accounts"][0]["cash"] = "0"
    data.update(outside_cash="0", short_collateral_fraction="0", cover_stock_calls=False)
    data["marks"][-1].update(stock="100", index="1000")
    result = run(parse(data))
    assert result["ending"]["cash"] == -79500
    assert result["ending"]["wealth"] == -79500
    assert result["ending"]["loan"] == 0
    assert result["ending"]["shares"] == 0
