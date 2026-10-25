"""Both policies see one immutable batch; future prices cannot alter past trades."""

import pytest

from wealthlab.markets.household_run import paired, run
from wealthlab.markets.inputs import MarketCase
from wealthlab.markets.paths import generate
from wealthlab.markets.rebalance_example import hold, synthetic


@pytest.mark.parametrize("mode", ["deterministic", "historical", "monte_carlo", "stress"])
def test_all_four_methods_share_realized_paths_without_changing_source(mode):
    scenario, market, binding = synthetic(mode)
    source = scenario.model_dump_json()
    batch = generate(market)
    before = batch.export()
    left = run(scenario, batch, binding, [0])
    right = run(hold(scenario), batch, binding, [0])
    assert paired(left, right)[0]["path"] == 0
    assert left["details"][0]["rows"][-1]["lot_audit"]["rebalance_decisions"]
    assert not right["details"][0]["rows"][-1]["lot_audit"]["rebalance_decisions"]
    assert batch.export() == before
    assert scenario.model_dump_json() == source


def test_last_month_crash_cannot_rewrite_prior_decisions_or_cash():
    scenario, market, binding = synthetic()
    data = market.model_dump(mode="json")
    data.update(
        mode="stress", shocks=[dict(name="late", month=23, mark_shocks=dict(equities=-0.8))]
    )
    normal = run(scenario, generate(market), binding, [0])["details"][0]["rows"]
    crashed = run(scenario, generate(MarketCase.model_validate(data)), binding, [0])["details"][0][
        "rows"
    ]
    assert normal[:-1] == crashed[:-1]
    assert normal[-1]["net_wealth"] != crashed[-1]["net_wealth"]
    assert (
        normal[-1]["lot_audit"]["rebalance_decisions"]
        == crashed[-1]["lot_audit"]["rebalance_decisions"]
    )
