"""Own and survivor benefits are not added in full; an early widow reduction stays fixed.

Only the auxiliary excess remains when a worker begins their own benefit.
A later larger own benefit can replace it, without recovering the early widow
reduction or erasing cash issued before that claim date.
"""

from datetime import date
from decimal import Decimal

from tests.test_social_cash import cash_row
from tests.test_survivor_cash import calculate, payload


def test_larger_own_claim_replaces_survivor_cash_without_adding_both():
    result = calculate(payload())
    before = cash_row(result, "spouse", date(2035, 1, 1))
    after = cash_row(result, "spouse", date(2035, 2, 1))
    assert before["issued_before_offsets"] == 3036
    assert after["own_with_delayed_credits"] == 3720
    assert after["survivor_before_own_offset"] == Decimal("3036.80")
    assert after["survivor_excess"] == 0
    assert after["issued_before_offsets"] == 3720


def test_smaller_own_claim_reduces_only_the_survivor_excess():
    data = payload()
    data["members"][1]["pia_january_2026"] = 1000
    after = cash_row(calculate(data), "spouse", date(2035, 2, 1))
    assert after["own_with_delayed_credits"] == 1240
    assert after["survivor_excess"] == Decimal("1796.80")
    assert after["issued_before_offsets"] == 3036


def test_denied_survivor_eligibility_is_an_explicit_zero_not_an_automatic_award():
    data = payload()
    data["members"][1]["survivor_eligibility_confirmed"] = False
    row = cash_row(calculate(data), "spouse", date(2032, 1, 1))
    assert row["survivor_excess"] == 0
    assert row["issued_before_offsets"] == 0


def test_survivor_cash_stops_at_its_own_death_with_last_valid_arrears_preserved():
    data = payload()
    data["members"][1]["death_date"] = "2033-04-15"
    result = calculate(data)
    assert cash_row(result, "spouse", date(2033, 4, 1))["issued_before_offsets"] == 3036
    assert cash_row(result, "spouse", date(2033, 5, 1))["issued_before_offsets"] == 0
