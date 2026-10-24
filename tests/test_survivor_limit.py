"""RIB-LIM caps the age-reduced amount, instead of multiplying an already capped amount."""

from datetime import date
from decimal import Decimal

from tests.test_social_cash import cash_row
from tests.test_survivor_cash import calculate
from wealthlab.retirement.social import run
from wealthlab.retirement.survivor_example import early_limit


def test_fra_survivor_is_limited_by_early_workers_82_point_5_percent_floor():
    result = run(early_limit())
    row = cash_row(result, "spouse", date(2026, 10, 1))
    assert result["total_issued_before_offsets"] == 82980
    assert row["survivor_after_age_reduction"] == 2500
    assert row["survivor_worker_limit"] == Decimal("2062.50")
    assert row["survivor_excess"] == Decimal("2062.50")
    assert row["issued_before_offsets"] == 2062


def test_age_reduction_precedes_the_limit_and_does_not_disappear_at_fra():
    data = early_limit().model_dump(mode="json")
    data["end_year"] = 2035
    data["members"][1].update(
        birth_date="1966-01-02", claim_month="2036-01-01", survivor_claim_month="2026-01-01"
    )
    result = calculate(data)
    first = cash_row(result, "spouse", date(2026, 2, 1))
    later = cash_row(result, "spouse", date(2033, 2, 1))
    assert first["survivor_worker_limit"] == Decimal("2062.50")
    assert first["survivor_after_age_reduction"] == Decimal("1787.50")
    assert first["survivor_excess"] == later["survivor_excess"] == Decimal("1787.50")


def test_workers_larger_actual_reduced_benefit_can_set_the_limit():
    data = early_limit().model_dump(mode="json")
    data["members"][0]["claim_month"] = "2025-01-01"
    row = cash_row(calculate(data), "spouse", date(2026, 10, 1))
    assert row["survivor_worker_limit"] == Decimal("2166.60")
    assert row["issued_before_offsets"] == 2166
