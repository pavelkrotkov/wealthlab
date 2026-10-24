"""Illiquidity keeps marked wealth but prevents sales needed for actual spending."""

from wealthlab.markets.household_example import synthetic
from wealthlab.markets.household_run import paired, run
from wealthlab.markets.inputs import MarketCase
from wealthlab.markets.paths import generate


def test_lock_prevents_funding_and_preserves_shares_without_erasing_value():
    case, market, binding = synthetic()
    data = market.model_dump(mode="json")
    data.update(
        mode="stress", shocks=[dict(name="synthetic lock", month=0, lock_months=dict(equities=24))]
    )
    result = run(case, generate(MarketCase.model_validate(data)), binding)
    rows = result["details"][0]["rows"]
    assert not result["outcomes"][0]["funded"]
    assert result["outcomes"][0]["first_failure"] == "2026-05-01"
    assert sum(r["lot_funding_proceeds"] for r in rows) == 0
    assert rows[-1]["account_balances"]["brokerage"] > 100000
    assert rows[-1]["lot_audit"]["lots"][0]["quantity"] == "400"
    assert result["aggregate"]["monte_carlo_95_wilson"] is None


def test_same_batch_pairs_actual_spending_policies():
    case, market, binding = synthetic("monte_carlo")
    batch = generate(market)
    left = run(case, batch, binding, indices=[0, 2])
    cheaper = case.model_copy(update=dict(expenses=[]))
    right = run(cheaper, batch, binding, indices=[0, 2])
    differences = paired(left, right)
    assert [r["path"] for r in differences] == [0, 2]
    assert all(r["real_wealth_change"] > 100000 for r in differences)
    assert left["aggregate"]["monte_carlo_95_wilson"] is not None
