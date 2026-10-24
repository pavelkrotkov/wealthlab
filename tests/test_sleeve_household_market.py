"""A shared-path squeeze changes real household funding, debt and unknown concentration coverage."""

from sleeve_market_cases import baseline

from wealthlab.household.scenario import Scenario
from wealthlab.markets.household_run import paired, run
from wealthlab.markets.inputs import MarketCase
from wealthlab.markets.paths import generate


def test_paired_funding_keeps_recoursedebt_and_cannot_claim_complete_issuer_inventory():
    household, market, binding = baseline()
    data = market.model_dump(mode="json")
    data.update(mode="stress", shocks=[dict(name="squeeze", month=0, mark_shocks=dict(short=4))])
    batch = generate(MarketCase.model_validate(data))
    left = run(household, batch, binding)
    other = household.model_dump(mode="json")
    other["sleeve_plan"]["sleeves"][0]["case"].update(long_multiple=1, short_multiple=0)
    right = run(Scenario.model_validate(other), batch, binding)
    assert left["outcomes"][0]["funded"]
    assert not left["outcomes"][0]["product_feasible"]
    assert not left["outcomes"][0]["joint_feasible"]
    assert left["outcomes"][0]["funding_shortfall"] == 0
    assert left["outcomes"][0]["product_negative_equity_months"] == 12
    assert not left["outcomes"][0]["issuer_concentration_complete"]
    assert paired(left, right)[0]["real_wealth_change"] == 120000


def test_binding_does_not_mutate_source_observations():
    household, market, binding = baseline()
    original = household.model_dump_json()
    run(household, generate(market), binding)
    assert household.model_dump_json() == original
