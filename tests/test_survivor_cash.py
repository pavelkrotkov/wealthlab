"""Survivor entitlements preserve death-month arrears and can switch to a larger own benefit."""

from datetime import date

from tests.test_social_cash import cash_row
from wealthlab.retirement.social import run
from wealthlab.retirement.social_inputs import SocialCase
from wealthlab.retirement.survivor_example import switch_case


def payload():
    return switch_case().model_dump(mode="json")


def calculate(data):
    return run(SocialCase.model_validate(data))


def test_synthetic_survivor_then_own_cash_matches_independent_month_counts():
    result = run(switch_case())
    # Seven worker checks,42 reduced-survivor checks,23 larger own checks.
    assert result["total_issued_before_offsets"] == 7 * 3100 + 42 * 3036 + 23 * 3720
    assert result["total_issued_before_offsets"] == 234772
    assert result["owl_comparison"]["status"] == "outside_reference_scope"


def test_prior_month_worker_check_survives_but_death_month_entitlement_does_not():
    result = run(switch_case())
    assert cash_row(result, "person", date(2031, 7, 1))["issued_before_offsets"] == 3100
    assert cash_row(result, "person", date(2031, 8, 1))["issued_before_offsets"] == 0
    assert cash_row(result, "spouse", date(2031, 7, 1))["issued_before_offsets"] == 0
    assert cash_row(result, "spouse", date(2031, 8, 1))["issued_before_offsets"] == 3036


def test_year_end_death_moves_first_survivor_cash_into_the_following_year():
    data = payload()
    data["members"][0]["death_date"] = "2031-12-15"
    data["members"][1]["survivor_claim_month"] = "2031-12-01"
    result = calculate(data)
    assert cash_row(result, "person", date(2031, 12, 1))["issued_before_offsets"] == 3100
    assert cash_row(result, "person", date(2032, 1, 1))["issued_before_offsets"] == 0
    assert cash_row(result, "spouse", date(2031, 12, 1))["issued_before_offsets"] == 0
    assert cash_row(result, "spouse", date(2032, 1, 1))["survivor_excess"] > 0
