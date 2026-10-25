"""Realized plan marks and locks feed the same required-withdrawal and tax books.

RMD cash transfers do not themselves destroy wealth. For each actual path,
ending wealth equals initial assets plus actual plan returns minus reported
tax liability. A lock lasting through the deadline must fail the policy even
when there was no ordinary spending request.
"""

from decimal import Decimal

import pytest

from wealthlab.markets.household_run import run
from wealthlab.markets.paths import generate
from wealthlab.markets.workplace_rmd_example import synthetic
from wealthlab.tax.household_reporting import summary


@pytest.mark.parametrize("mode", ["deterministic", "historical", "monte_carlo", "stress"])
def test_required_withdrawals_and_tax_reconcile_on_all_four_realized_path_methods(mode):
    household, market, binding = synthetic(mode)
    result = run(household, generate(market), binding, [0])
    rows = result["details"][0]["rows"]
    liability = summary(rows)["reported_tax_liability"]
    change = sum((r["workplace_market_change"] for r in rows), Decimal(0))
    assert rows[0]["workplace_rmd_required"] == 20000
    assert rows[-1]["net_wealth"] == 492000 + change - liability
    assert rows[11]["workplace_rmd_shortfall"] == 0
    assert result["outcomes"][0]["workplace_rmd_shortfall_total"] == 0


def test_whole_horizon_illiquidity_exposes_rmd_failure_timing_and_magnitude():
    household, market, binding = synthetic("stress", "illiquidity")
    result = run(household, generate(market), binding, [0])
    outcome = result["outcomes"][0]
    assert not outcome["funded"]
    assert outcome["first_workplace_rmd_failure"] == "2026-12-01"
    assert outcome["workplace_rmd_shortfall_total"] >= 20000
    assert outcome["workplace_rmd_unresolved_terminal"] == outcome["workplace_rmd_shortfall_total"]
    assert outcome["workplace_rmd_excise_tax_total"] > 0
