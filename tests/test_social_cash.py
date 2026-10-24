"""Issued benefits conserve entitlement timing without counting the next January early."""

from wealthlab.retirement.social import run
from wealthlab.retirement.social_example import synthetic
from wealthlab.retirement.social_inputs import SocialCase


def payload():
    return synthetic().model_dump(mode="json")


def calculate(data):
    return run(SocialCase.model_validate(data))


def test_synthetic_claims_keep_cash_month_and_final_entitlement_separate():
    result = run(synthetic())
    assert result["total_issued_before_offsets"] == 152250
    assert len(result["cash_months"]) == 72
    assert len(result["monthly_entitlements"]) == 74
    assert result["cash_months"][0]["issued_before_offsets"] == 0
    assert result["monthly_entitlements"][-1]["issued_before_offsets"] == 1250
    assert result["monthly_entitlements"][-1]["payment_month"].year == 2033


def cash_row(result, member, month):
    return next(
        row
        for row in result["cash_months"]
        if row["member"] == member and row["payment_month"] == month
    )
