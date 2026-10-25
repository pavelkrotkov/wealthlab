"""Actual options, shares, collateral and federal/NJ cash execute on identical realized paths."""

import pytest

from tests.option_market_cases import flat
from wealthlab.markets.household_run import paired, run


@pytest.mark.parametrize(
    "strategy,expected",
    [("Covered call", 24600), ("Collar", 24200), ("Four-leg synthetic exposure", 23800)],
)
def test_flat_path_exact_exit_cash_and_no_premium_double_count(strategy, expected):
    scenario, batch, binding = flat(strategy)
    result = run(scenario, batch, binding)
    final = result["details"][0]["rows"][-1]
    assert final["closing_cash"] == expected
    assert final["net_wealth"] == expected
    assert final["option_shares"] == final["option_collateral"] == 0
    assert result["outcomes"][0]["option_feasible"]
    assert result["batch_id"] == batch.metadata["batch_id"]


def test_policy_comparison_reuses_same_realized_batch_and_actual_tax_cash():
    collar, batch, binding = flat("Collar")
    four_leg, _, other_binding = flat()
    left, right = run(collar, batch, binding), run(four_leg, batch, other_binding)
    difference = paired(left, right)[0]
    assert difference["real_wealth_change"] == -400
    assert difference["net_cash_taxes_paid_change"] == 0
    assert left["indices"] == right["indices"] == [0]
