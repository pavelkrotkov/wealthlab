"""Delay comparisons retain the fund asset returns, leverage, financing and fee schedule."""

from decimal import Decimal

from qoz_cases import flat

from wealthlab.products.qoz_compare import compare


def test_timely_and_delayed_exits_differ_only_after_the_same_actual_sale_request():
    result = compare(flat())
    delayed = result["rows"]["allowed"][-1]["qoz_audit"]
    timely = result["rows"]["timely_exit"][-1]["qoz_audit"]
    assert delayed["terms"]["economics"] == timely["terms"]["economics"]
    assert delayed["terms"]["observations"] == timely["terms"]["observations"]
    assert delayed["terms"]["preferred_hurdle"] == timely["terms"]["preferred_hurdle"]
    assert delayed["terms"]["carry_fraction"] == timely["terms"]["carry_fraction"]
    assert result["rows"]["timely_exit"][-2]["qoz_settlement_cash"] == Decimal(80000)
    assert result["rows"]["allowed"][-2]["qoz_settlement_cash"] == 0
    assert result["rows"]["allowed"][-1]["qoz_settlement_cash"] == Decimal(80000)
