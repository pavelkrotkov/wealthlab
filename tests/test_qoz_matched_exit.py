"""Delay comparisons retain the fund asset returns, leverage, financing and fee schedule."""

from decimal import Decimal

import pytest
from qoz_cases import edited, flat

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


@pytest.mark.parametrize("entered", ["denied", "deferred"])
def test_timely_exit_matches_the_named_allowed_policy_even_when_entered_tax_choice_differs(entered):
    result = compare(edited(flat(), federal=entered))
    timely_call = result["rows"]["timely_exit"][-1]["qoz_audit"]["calls"][0]
    allowed_call = result["rows"]["allowed"][-1]["qoz_audit"]["calls"][0]
    denied_call = result["rows"]["denied"][-1]["qoz_audit"]["calls"][0]
    assert timely_call["elected"]["federal"] == Decimal(80000)
    assert allowed_call["elected"] == timely_call["elected"]
    assert denied_call["elected"]["federal"] == 0
