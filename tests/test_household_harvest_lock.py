"""A tradable loss cannot force purchase of a replacement whose market is locked."""

from tests.market_household_cases import flat
from wealthlab.markets.household_run import run
from wealthlab.markets.inputs import MarketCase
from wealthlab.markets.paths import generate
from wealthlab.markets.policy_example import enable


def test_replacement_liquidity_is_required_for_the_actual_pair():
    case, market, binding = flat(cash_yield=0)
    case, binding = enable(case, binding, "Harvesting")
    payload = market.model_dump(mode="json")
    payload["assets"].append(dict(payload["assets"][0], id="replacement_factor"))
    payload["correlation"] = [[1, 0, 0], [0, 1, 0], [0, 0, 1]]
    payload.update(
        mode="stress",
        shocks=[
            dict(
                name="loss and replacement lock",
                month=0,
                mark_shocks=dict(equities=-0.5),
                lock_months=dict(replacement_factor=1),
            )
        ],
    )
    replacement = binding.securities[1].model_copy(update=dict(factor="replacement_factor"))
    binding = binding.model_copy(update=dict(securities=[binding.securities[0], replacement]))
    rows = run(case, generate(MarketCase.model_validate(payload)), binding)["details"][0]["rows"]
    audit = rows[-1]["lot_audit"]
    assert "replacement blocked" in audit["harvest_decisions"][0]["status"]
    assert audit["trades"] == []
    assert rows[-1]["net_wealth"] == 51000
    assert rows[-1]["annual_tax"]["federal"]["long_carry"] == 0
