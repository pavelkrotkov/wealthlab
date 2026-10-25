"""Historical and correlated Monte Carlo paths reuse the same current-wage capacity rules."""

import pytest

from wealthlab.markets.household_run import run
from wealthlab.markets.hsa_payroll_example import synthetic
from wealthlab.markets.paths import generate


@pytest.mark.parametrize("mode", ["historical", "monte_carlo"])
def test_realized_work_changes_feed_actual_salary_reductions_without_future_wages(mode):
    household, market, binding = synthetic(mode)
    batch = generate(market)
    result = run(household, batch, binding, [0])
    rows = result["details"][0]["rows"]
    assert result["batch_id"] == batch.metadata["batch_id"]
    assert result["outcomes"][0]["hsa_salary_reductions"] == sum(
        500 for row in rows if row["income"] > 0
    )
    assert all(row["hsa_payroll_contributions"] <= row["income"] for row in rows)
    assert result["outcomes"][0]["provisional_tax_years"] == []
