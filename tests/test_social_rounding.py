"""SSA rounds each payable record separately and preserves a benefit smaller than one dollar.

POMS RS00601.020D.2 requires rounding after dual-entitlement reductions on each
benefit. D.3 excepts a positive amount below one dollar from lower-dollar rounding.
"""

from datetime import date
from decimal import Decimal

import pytest

from tests.test_social_cash import calculate, cash_row, payload
from tests.test_survivor_cash import calculate as survivor_calculate
from tests.test_survivor_cash import payload as survivor_payload
from wealthlab.retirement.social_amounts import dollar


@pytest.mark.parametrize(("before", "after"), [("0", "0"), (".9", ".9"), ("1.9", "1")])
def test_sub_dollar_exception_and_regular_lower_dollar_rounding(before, after):
    assert dollar(Decimal(before)) == Decimal(after)


def test_own_and_spouse_records_are_rounded_after_their_separate_reductions():
    data = payload()
    data.update(start_year=2026, end_year=2027)
    for person in data["members"]:
        person["claim_month"] = "2022-01-01"
    data["members"][1]["pia_january_2026"] = "1001.10"
    row = cash_row(calculate(data), "spouse", date(2026, 2, 1))
    assert row["own_with_delayed_credits"] == Decimal("700.70")
    assert row["spousal_excess"] == Decimal("161.70")
    assert row["issued_before_offsets"] == 861


def test_own_and_survivor_excess_do_not_recover_each_others_truncated_cents():
    data = survivor_payload()
    data["members"][1]["pia_january_2026"] = "1000.80"
    row = cash_row(survivor_calculate(data), "spouse", date(2035, 2, 1))
    assert row["own_with_delayed_credits"] == Decimal("1240.90")
    assert row["survivor_excess"] == Decimal("1795.90")
    assert row["issued_before_offsets"] == 3035
