"""Supplied SE and AMT facts affect actual tax independently from ordinary partnership income."""

from decimal import Decimal

from ordinary_income_cases import compute


def test_supplied_box14_earnings_drive_se_tax_deduction_and_net_qbi_once():
    result = compute(
        dict(
            wages_primary=50000,
            allowed_nonpassive_partnership_income=10000,
            partnership_se_earnings_primary=10000,
            partnership_qbi_before_se_deduction=10000,
        )
    )
    details = result["partnership"]
    assert details["self_employment_tax"] == Decimal("1412.96")
    assert details["deductible_se_tax"] == Decimal("706.48")
    assert result["agi"] == Decimal("59293.52")
    assert details["qbi_deduction"] == Decimal("1858.70")


def test_se_social_security_cap_uses_existing_wages_and_se_medicare_remains_due():
    result = compute(
        dict(
            wages_primary=200000,
            allowed_nonpassive_partnership_income=10000,
            partnership_se_earnings_primary=10000,
        )
    )
    assert result["partnership"]["self_employment_tax"] == Decimal("267.82")
    assert result["additional_medicare"] == Decimal("83.12")


def test_supplied_amt_preference_keeps_regular_agi_and_computes_current_amt():
    result = compute(dict(wages_primary=100000, additional_amt_income=100000))
    # 2025 Form 6251: ($200k AMTI - $88,100 single exemption) * 26% = $29,094.
    assert result["agi"] == 100000
    assert result["income_tax"] == 29094
    assert result["amt"] == 15645


def test_all_partnership_channels_clear_between_cached_households():
    compute(
        dict(
            allowed_nonpassive_partnership_income=50000,
            partnership_se_earnings_primary=50000,
            partnership_qbi_before_se_deduction=50000,
            additional_amt_income=100000,
        )
    )
    empty = compute({})
    assert empty["total"] == 0
    assert empty["partnership"]["self_employment_tax"] == 0
    assert empty["partnership"]["qbi_deduction"] == 0
    assert empty["amt"] == 0
