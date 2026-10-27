"""An actual native stock sale supplies cash once and preserves three independent tax bases."""

from decimal import Decimal

from wealthlab.tax.jurisdiction_execution import evaluate
from wealthlab.tax.pr_execution_gain_example import synthetic_gain


def test_actual_sale_and_monthly_wages_keep_source_basis_and_physical_cash_conservation():
    result = evaluate(synthetic_gain())
    rows, final = result["rows"], result["rows"][-1]
    assert rows[0]["account_balances"]["brokerage"] == 25000
    assert rows[1]["account_balances"]["brokerage"] == 0
    assert final["lot_audit"]["lots"] == []
    disposal = final["lot_audit"]["disposals"][0]
    assert (disposal["proceeds"], disposal["federal_gross_gain"], disposal["nj_gross_gain"]) == (
        25000,
        10000,
        9000,
    )
    audit = result["country_assessments"]["es_income_2025"]["gain_allocations"][0]
    assert (audit["federal_us"], audit["federal_pr"], audit["pr_pre"], audit["pr_post"]) == (
        5000,
        5000,
        7000,
        5000,
    )
    total_paid = sum(
        r["foreign_tax_paid"]
        + r["tax_withheld"]
        + r["tax_estimates_paid"]
        + r["tax_settlement_paid"]
        + r["prior_tax_paid"]
        + r["essential"]
        for r in rows
    )
    assert final["net_wealth"] == 75000 + 40000 - total_paid


def test_ordinary_and_conditional_decree_keep_actual_sale_cash_and_compliance_cost_identical():
    ordinary = evaluate(synthetic_gain("ordinary"))
    incentive = evaluate(synthetic_gain("incentive"))
    old, new = ordinary["rows"][-1], incentive["rows"][-1]
    assert old["annual_tax"]["federal"]["income_tax"] == new["annual_tax"]["federal"]["income_tax"]
    assert old["annual_tax"]["new_jersey"] == new["annual_tax"]["new_jersey"]
    assert old["net_wealth"] < new["net_wealth"]
    assert new["net_wealth"] - old["net_wealth"] == Decimal("750")
    assert not new["funding_failure"]
