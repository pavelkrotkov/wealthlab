"""A survivor receives pre-claim DRCs the deceased worker had not yet had credited to cash."""

from datetime import date
from decimal import Decimal

from tests.test_social_cash import cash_row
from tests.test_survivor_cash import calculate, payload


def drc_case(claim, death, survivor_start):
    data = payload()
    data.update(start_year=2028, end_year=2031)
    data["members"][0].update(claim_month=claim, death_date=death)
    data["members"][1].update(
        birth_date="1960-01-02",
        pia_january_2026=1000,
        claim_month="2030-01-01",
        survivor_claim_month=survivor_start,
    )
    return data


def test_death_before_worker_claim_preserves_earned_delayed_credits():
    data = drc_case("2030-01-01", "2028-07-15", "2028-07-01")
    result = calculate(data)
    row = cash_row(result, "spouse", date(2028, 8, 1))
    assert row["inherited_delayed_credits"] == 300
    assert row["survivor_excess"] == 2800
    assert cash_row(result, "person", date(2030, 2, 1))["issued_before_offsets"] == 0


def test_current_year_worker_credit_delay_does_not_reduce_the_survivors_original_amount():
    data = drc_case("2028-07-01", "2028-09-15", "2028-09-01")
    result = calculate(data)
    before = cash_row(result, "person", date(2028, 9, 1))
    after = cash_row(result, "spouse", date(2028, 10, 1))
    assert before["issued_before_offsets"] == 2700
    assert after["inherited_delayed_credits"] == 300
    assert after["survivor_original"] == 2800


def test_separate_survivor_fra_can_precede_own_retirement_fra():
    data = drc_case("2030-01-01", "2028-07-15", "2028-07-01")
    data.update(start_year=2026, end_year=2028)
    data["members"][0]["death_date"] = "2026-09-15"
    data["members"][1]["survivor_claim_month"] = "2026-09-01"
    row = cash_row(calculate(data), "spouse", date(2026, 10, 1))
    assert row["survivor_after_age_reduction"] == Decimal(2500)
    assert row["issued_before_offsets"] == 2500
