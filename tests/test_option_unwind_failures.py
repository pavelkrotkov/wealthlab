"""A failed executable stock exit retains the actual position and visible obligation."""

from tests.option_cases import one_leg, parse
from wealthlab.products.option_engine import run


def test_stock_exit_fee_above_gross_proceeds_returns_incomplete_unwind_not_a_crash():
    data = one_leg(unwind=True)
    data["marks"][-1]["stock"] = "0.001"
    data["stock_sale_fee"] = "1"
    result = run(parse(data))
    assert result["ending"]["shares"] == 100
    assert result["ending"]["phase"] == "unwind_incomplete"
    assert "Sale commission exceeds gross proceeds" in result["failures"][0]
    assert not result["open_legs"]
