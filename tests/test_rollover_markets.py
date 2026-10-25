"""Realized plan and IRA returns conserve assets across actual dated transfers in every mode."""

from decimal import Decimal

import pytest

from wealthlab.markets.household_run import run
from wealthlab.markets.paths import generate
from wealthlab.markets.rollover_example import synthetic


@pytest.mark.parametrize("mode", ["deterministic", "historical", "monte_carlo", "stress"])
def test_actual_rollovers_and_ira_withdrawals_share_realized_market_paths(mode):
    household, market, binding = synthetic(mode)
    result = run(household, generate(market), binding, [0])
    rows = result["details"][0]["rows"]
    outcome = result["outcomes"][0]
    transferred = min(Decimal(80000), rows[0]["account_balances"]["work_pretax"])
    gains = sum(r["workplace_market_change"] for r in rows)
    gains += sum(r.get("ira_annual_reconciliation", {}).get("market_change", 0) for r in rows)
    assert outcome["workplace_rollover_funded_total"] == transferred
    assert outcome["workplace_rollover_unfilled_total"] == 80000 - transferred
    assert rows[2]["ira_withdrawal_cash"] == 15000
    assert rows[-1]["net_wealth"] == 120000 + gains - outcome["reported_tax_liability"]
    assert rows[-1]["workplace_rollover_audit"][0]["source_rmd_unresolved"] == 0
