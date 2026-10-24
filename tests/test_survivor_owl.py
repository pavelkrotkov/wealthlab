"""A full calendar year after death and survivor FRA is a supported limited Owl comparison.

The death year is excluded because Owl uses a full-year convention rather than
monthly entitlement in arrears. No DRC, deduction, COLA or rounding gap applies
when the unreduced integer survivor benefit dominates the recipient's own.
"""

import numpy as np

from tests.test_survivor_cash import calculate, payload


def test_supported_full_year_unreduced_survivor_amount_matches_owl():
    from owlplanner.socialsecurity import compute_survivor_stream

    data = payload()
    data.update(start_year=2026, end_year=2031)
    data["members"][0].update(claim_month="2027-01-01", death_date="2028-01-15")
    data["members"][1].update(
        birth_date="1959-01-02",
        pia_january_2026=1000,
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
        np.array([2500, 1000]),
        np.array([67, 70]),
        np.array([1960, 1959]),
        np.array([1, 1]),
        np.array([2, 2]),
        np.array([2, 5]),
        2,
        5,
        thisyear=2026,
    )
    assert native == reference.annual[3] == 30000
