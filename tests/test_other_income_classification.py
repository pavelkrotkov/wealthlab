"""Other income changes MAGI/SSA without generating NII, payroll, QBI or earned credits."""

import pytest
from ordinary_income_cases import compute

from wealthlab.tax.federal_engine import values


def test_noninvestment_income_is_not_added_to_niit_investment_base():
    result = compute(
        dict(wages_primary=250000, interest=30000, ordinary_noninvestment_income=50000)
    )
    # NIIT is 3.8% of $30k; additional Medicare applies only to actual $250k wages.
    assert (result["niit"], result["additional_medicare"]) == (1140, 450)
    assert result["agi"] == 330000


def test_other_income_participates_in_social_security_taxability():
    result = compute(dict(social_security=30000, ordinary_noninvestment_income=50000), age=67)
    assert (result["taxable_social_security"], result["agi"]) == (25500, 75500)


@pytest.mark.parametrize("amount", [15000, 100000])
def test_carrier_does_not_generate_earned_income_credit_or_business_deduction(amount):
    data = dict(RECID=1, MARS=1, XTOT=1, age_head=40, e00800=amount)
    result = values(data, 2025, ("eitc", "qbided", "ptax_was", "c00100"))
    assert result == dict(eitc=0, qbided=0, ptax_was=0, c00100=amount)


def test_cached_calculator_clears_other_income_before_the_next_household():
    data = dict(RECID=1, MARS=1, XTOT=1, age_head=40, e00800=10000)
    assert values(data, 2025, ("c00100",))["c00100"] == 10000
    assert values(dict(data, e00800=0), 2025, ("c00100",))["c00100"] == 0
