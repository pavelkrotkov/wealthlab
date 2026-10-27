"""A conditional4% profile cannot override a computed cheaper ordinary statutory alternative."""

from pr_execution_small_gain import small_gain

from wealthlab.tax.jurisdiction_execution import evaluate


def test_actual_small_sale_selects_zero_ordinary_tax_instead_of_four_percent_incentive():
    result = evaluate(small_gain())
    audit = result["country_assessments"]["es_income_2025"]
    final = result["rows"][-1]
    assert audit["assessment"]["income_tax"] == 0
    assert audit["selected_treatment"] == "more_favorable_ordinary"
    assert final["lot_audit"]["disposals"][0]["proceeds"] == 101000
    assert final["net_wealth"] == 150750
    assert not final["funding_failure"]
