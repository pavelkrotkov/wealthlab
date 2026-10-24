"""Unsupported history is a blocking condition, not a zero work deduction or assumed eligibility."""

import pytest

from tests.test_social_cash import calculate, payload


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("birth_date", "1943-01-01"),
        ("birth_date", "2031-01-01"),
        ("claim_month", "2021-12-01"),
        ("claim_month", "2030-01-02"),
        ("provenance", "unresolved"),
        ("pia_january_2026", "1000.01"),
        ("partner", "unknown"),
        ("partner", "person"),
        ("partner", None),
        ("own_insured", False),
    ],
)
def test_invalid_or_unsupported_member_fails(field, value):
    data = payload()
    data["members"][0][field] = value
    with pytest.raises(ValueError):
        calculate(data)


def test_missing_work_test_confirmation_blocks_the_ordinary_claim_case():
    data = payload()
    data["no_earnings_test_deductions_confirmed"] = False
    with pytest.raises(ValueError, match="no earnings-test deductions"):
        calculate(data)


def test_partner_references_and_ids_cannot_be_ambiguous():
    data = payload()
    data["members"][1]["partner"] = None
    with pytest.raises(ValueError, match="reciprocal"):
        calculate(data)
    data = payload()
    data["members"][1]["id"] = "person"
    with pytest.raises(ValueError, match="unique"):
        calculate(data)


def test_unmodeled_record_auxiliaries_cannot_silently_skip_family_maximum_rules():
    data = payload()
    data["no_other_auxiliaries_confirmed"] = False
    with pytest.raises(ValueError, match="no other record auxiliaries"):
        calculate(data)
