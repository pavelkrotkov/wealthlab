"""Identical annual facts make actual surrender tax reduce spendable cash once."""

from decimal import Decimal

from wealthlab.products.life_allocation_example import synthetic
from wealthlab.products.life_comparison import compare


def test_actual_exit_tax_reduces_the_cash_advantage_under_the_same_annual_facts():
    from wealthlab.products.life_comparison_inputs import LifeComparison

    data = synthetic().model_dump(mode="json")
    for scenario in data["alternatives"].values():
        scenario["accounts"][0]["balance"] = "100000"
        annual = scenario["tax_plan"]["cases"][0]
        annual["federal_income"]["interest"] = "200000"
        annual["nj_income"]["interest"] = "200000"
        scenario["tax_plan"]["settlement_timing"] = "monthly_accrued"
    result = compare(LifeComparison.model_validate(data))
    outcomes = {k: v["outcomes"][0] for k, v in result["alternatives"].items()}
    extra_tax = (
        outcomes["new_issue"]["reported_tax_liability"]
        - outcomes["no_policy"]["reported_tax_liability"]
    )
    assert extra_tax == Decimal("28.37")
    assert result["differences"]["new_issue"][0]["marked_wealth_change"] == 100 - extra_tax
    assert (
        outcomes["new_issue"]["net_cash_taxes_paid"] - outcomes["no_policy"]["net_cash_taxes_paid"]
        == extra_tax
    )
