"""The insurance NIIT kernel preserves supplied partnership classifications and earnings."""

from decimal import Decimal

from ordinary_income_cases import compute


def test_nonpassive_loss_does_not_erase_policy_niit_but_passive_loss_can_net_it():
    income = dict(wages_primary=300000, interest=30000, insurance_ordinary_income=10000)
    nonpassive = compute(dict(income, allowed_nonpassive_partnership_income=-50000))
    passive = compute(dict(income, allowed_passive_income=-50000))
    assert (nonpassive["agi"], passive["agi"]) == (290000, 290000)
    assert (nonpassive["niit"], passive["niit"]) == (1520, 0)
    assert nonpassive["partnership"]["qbi_deduction"] == 0


def test_policy_income_preserves_independent_se_deduction_and_eligible_qbi():
    result = compute(
        dict(
            wages_primary=50000,
            insurance_ordinary_income=10000,
            allowed_nonpassive_partnership_income=10000,
            partnership_se_earnings_primary=10000,
            partnership_qbi_before_se_deduction=10000,
        )
    )
    facts = result["partnership"]
    assert result["agi"] == Decimal("69293.52")
    assert (facts["self_employment_tax"], facts["deductible_se_tax"]) == (
        Decimal("1412.96"),
        Decimal("706.48"),
    )
    assert facts["qbi_deduction"] == Decimal("1858.70")
    assert result["niit"] == 0
