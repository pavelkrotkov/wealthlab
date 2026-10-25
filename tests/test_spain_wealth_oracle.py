"""AEAT's 2025 Toledo worked example fixes the expected IP cap independently."""

from decimal import Decimal

from wealthlab.tax.spain import evaluate
from wealthlab.tax.spain_example import synthetic


def test_official_toledo_ip_limit_and_nonproductive_quota():
    wealth = evaluate(synthetic())["wealth"]["assessment"]
    assert wealth["wealth"]["gross_quota"] == Decimal("112354.37")
    assert wealth["wealth"]["nonproductive_quota"] == Decimal("3511.07")
    assert wealth["wealth"]["cap_eligible_quota"] == Decimal("108843.30")
    assert (wealth["adjusted_irpf_quota"], wealth["combined_ceiling"]) == (12597, 30600)
    assert wealth["wealth"]["cap_reduction"] == Decimal("89883.50")
    assert wealth["wealth_liability"] == Decimal("22470.87")
