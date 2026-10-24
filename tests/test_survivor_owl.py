"""A full calendar year after death and survivor FRA is a supported limited Owl comparison.

The death year is excluded because Owl uses a full-year convention rather than
monthly entitlement in arrears. Fractional own/excess records also distinguish
per-record SSA cash rounding from Owl's combined annual benefit. An integer-
record case remains a supported equality check, with no inherited credits/COLA.
"""

import numpy as np
import pytest

from tests.test_survivor_cash import calculate, payload


@pytest.mark.parametrize(
    ("pia", "own", "excess", "expected"),
    [(1000, "1253.3", "1246.7", 29989), (1500, "1880", "620", 30000)],
)
def test_full_year_survivor_reference_exposes_dual_record_rounding(pia, own, excess, expected):
    from owlplanner.socialsecurity import compute_survivor_stream

    data = payload()
    data.update(start_year=2026, end_year=2031)
    data["members"][0].update(claim_month="2027-01-01", death_date="2028-01-15")
    data["members"][1].update(
        birth_date="1959-01-02",
        pia_january_2026=pia,
        claim_month="2029-01-01",
        survivor_claim_month="2028-01-01",
    )
    result = calculate(data)
    native = next(
        r["issued_before_offsets"]
        for r in result["annual_cash"]
        if r["year"] == 2029 and r["member"] == "spouse"
    )
    reference = compute_survivor_stream(
        np.array([2500, pia]),
        np.array([67, 70]),
        np.array([1960, 1959]),
        np.array([1, 1]),
        np.array([2, 2]),
        np.array([2, 5]),
        2,
        5,
        thisyear=2026,
    )
    from datetime import date
    from decimal import Decimal

    from tests.test_social_cash import cash_row

    february = cash_row(result, "spouse", date(2029, 2, 1))
    assert february["own_with_delayed_credits"] == Decimal(own)
    assert february["survivor_excess"] == Decimal(excess)
    assert native == expected
    assert reference.annual[3] == 30000
