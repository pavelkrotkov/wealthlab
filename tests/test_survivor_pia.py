"""A pre62 death needs a supplied survivor PIA, distinct from a future retirement estimate."""

from datetime import date

import pytest

from tests.test_social_cash import cash_row
from tests.test_survivor_cash import calculate, payload


def young_worker():
    data = payload()
    data.update(start_year=2026, end_year=2028)
    data["members"][0].update(
        birth_date="1980-01-02",
        claim_month="2042-01-01",
        death_date="2026-01-15",
        spousal_eligibility_confirmed=False,
    )
    data["members"][1].update(
        birth_date="1960-01-02",
        pia_january_2026=0,
        own_insured=False,
        claim_month="2022-01-01",
        survivor_claim_month="2026-09-01",
    )
    return data


def test_missing_alternate_survivor_pia_blocks_instead_of_using_future_ordinary_pia():
    with pytest.raises(ValueError, match="Supply a survivor PIA"):
        calculate(young_worker())


def test_supplied_regular_death_pia_is_not_lifted_by_an_unearned_future_retirement_amount():
    data = young_worker()
    data["members"][0]["survivor_pia_january_2026"] = 1000
    row = cash_row(calculate(data), "spouse", date(2026, 10, 1))
    assert row["survivor_original"] == 1000
    assert row["inherited_delayed_credits"] == 0
    assert row["issued_before_offsets"] == 1000


def test_death_in_the_first_planned_early_claim_month_does_not_create_a_rib_limit():
    data = young_worker()
    data["members"][0].update(
        birth_date="1964-01-02", claim_month="2026-01-01", survivor_pia_january_2026=2500
    )
    row = cash_row(calculate(data), "spouse", date(2026, 10, 1))
    assert row["survivor_worker_limit"] is None
    assert row["issued_before_offsets"] == 2500
