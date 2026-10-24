"""Modern widow-before62 claims do not carry an early widow reduction into a later own claim."""

from datetime import date
from decimal import Decimal

from tests.test_social_cash import cash_row
from tests.test_survivor_cash import calculate, payload
from wealthlab.retirement.social_dates import earliest_survivor_month


def test_age60_survivor_can_later_take_a_larger_age70_own_benefit():
    data = payload()
    data.update(end_year=2043)
    data["members"][0]["death_date"] = "2031-01-15"
    data["members"][1].update(
        birth_date="1971-01-02", claim_month="2041-01-01", survivor_claim_month="2031-01-01"
    )
    result = calculate(data)
    first = cash_row(result, "spouse", date(2031, 2, 1))
    later = cash_row(result, "spouse", date(2041, 2, 1))
    assert first["survivor_excess"] == Decimal("2216.50")
    assert later["own_with_delayed_credits"] == 3720
    assert later["survivor_excess"] == 0
    assert later["issued_before_offsets"] == 3720


def test_survivor_age60_attainment_does_not_use_the_own_age62_full_month_rule():
    assert earliest_survivor_month(date(1960, 1, 1)) == date(2019, 12, 1)
    assert earliest_survivor_month(date(1960, 1, 3)) == date(2020, 1, 1)
