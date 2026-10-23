"""Retirement exclusions have different bases and owner-specific eligibility."""

from decimal import Decimal as D

import pytest

from wealthlab.tax.nj_retirement import RetirementEligibility, exclusions


def test_pension_and_other_exclusion_use_different_bases():
    """$40k pension + $80k investment income: $20k pension + $40k other.

    Pension cap is half of $40k, while the total unused cap is half of
    $120k minus the $20k already claimed. Taxable gross becomes $60k.
    """
    eligible = RetirementEligibility(qualified_pension=D(40000), age62_other_income=D(80000))
    result = exclusions(D(120000), D(40000), D(0), eligible, "joint")
    assert result == dict(pension_exclusion=D(20000), other_exclusion=D(40000))


def test_younger_spouse_income_cannot_use_older_spouse_exclusion():
    eligible = RetirementEligibility(qualified_pension=D(10000), age62_other_income=D(5000))
    result = exclusions(D(120000), D(40000), D(0), eligible, "joint")
    assert result == dict(pension_exclusion=D(10000), other_exclusion=D(5000))


@pytest.mark.parametrize(
    ("total", "employment", "expected"),
    [
        (100000, 3000, 60000),
        (100000, 3001, 0),
        (150001, 0, 0),
    ],
)
def test_other_exclusion_boundaries(total, employment, expected):
    eligible = RetirementEligibility(qualified_pension=D(40000), age62_other_income=D(60000))
    result = exclusions(D(total), D(40000), D(employment), eligible, "joint")
    assert result["other_exclusion"] == expected


def test_eligibility_amounts_are_bounded():
    with pytest.raises(ValueError, match="exceed"):
        exclusions(
            D(50000), D(10000), D(0), RetirementEligibility(qualified_pension=D(20000)), "single"
        )


def test_special_exclusion_can_reduce_remaining_pension_income():
    eligible = RetirementEligibility(qualified_pension=D(154000), special_exclusion_eligible=True)
    result = exclusions(D(154000), D(154000), D(0), eligible, "joint")
    assert result == dict(pension_exclusion=D(0), other_exclusion=D(6000))
