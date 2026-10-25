"""Actual path marks change the Roth earnings share; cost and withholding never become returns."""

from decimal import Decimal

import pytest

from wealthlab.markets.household_run import run
from wealthlab.markets.paths import generate
from wealthlab.markets.roth_cash_example import synthetic


@pytest.mark.parametrize("mode", ["deterministic", "historical", "monte_carlo", "stress"])
def test_designated_roth_cash_uses_actual_source_marks_and_separate_cost_in_every_mode(mode):
    household, market, binding = synthetic(mode)
    result = run(household, generate(market), binding, [0])
    rows = result["details"][0]["rows"]
    outcome = result["outcomes"][0]
    gross = min(Decimal(5000), rows[0]["account_balances"]["work_roth"])
    change = sum(r["workplace_market_change"] for r in rows)
    assert outcome["workplace_roth_gross_cash_total"] == gross
    assert rows[-1]["net_wealth"] == 10000 + change - outcome["reported_tax_liability"]
    audit = rows[-1]["workplace_roth_audit"][0]
    assert audit["federal_taxable"] >= 0
    assert outcome["workplace_roth_taxable_federal_total"] == audit["federal_taxable"]


def test_whole_horizon_illiquidity_leaves_cost_and_the_optional_failure_visible():
    household, market, binding = synthetic("stress", "illiquidity")
    result = run(household, generate(market), binding, [0])
    outcome = result["outcomes"][0]
    rows = result["details"][0]["rows"]
    assert outcome["workplace_roth_gross_cash_total"] == 0
    assert outcome["workplace_roth_unfilled_total"] == 5000
    assert outcome["first_unfilled_workplace_roth"] == "2026-02-01"
    assert rows[-1]["workplace_roth_contracts"][0]["federal_basis"] == 9400
    assert outcome["reported_tax_liability"] == 0
