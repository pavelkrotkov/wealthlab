"""Matched transfer policies retain batch identity; locked requests do not create assets."""

from wealthlab.household.scenario import Scenario
from wealthlab.markets.household_run import paired, run
from wealthlab.markets.paths import generate
from wealthlab.markets.rollover_example import synthetic


def test_partial_rollover_alternative_keeps_prices_and_total_wealth_matched():
    household, market, binding = synthetic()
    data = household.model_dump(mode="json")
    data["workplace_plan"]["cash_withdrawals"]["direct_rollovers"][0]["amount"] = 40000
    batch = generate(market)
    baseline = run(household, batch, binding, [0])
    other = run(Scenario.model_validate(data), batch, binding, [0])
    changes = paired(baseline, other)
    assert baseline["outcomes"][0]["workplace_rollover_funded_total"] == 80000
    assert other["outcomes"][0]["workplace_rollover_funded_total"] == 40000
    # Both books share a factor and can meet the withdrawal.
    # Moving the same assets between them alone adds no wealth.
    assert abs(changes[0]["real_wealth_change"]) <= 1
    assert changes[0]["reported_tax_liability_change"] == 0


def test_whole_horizon_source_and_ira_illiquidity_is_visible_without_retry():
    household, market, binding = synthetic("stress", "illiquidity")
    batch = generate(market)
    result = run(household, batch, binding, [0])
    outcome = result["outcomes"][0]
    audit = result["details"][0]["rows"][-1]["workplace_rollover_audit"]
    assert outcome["workplace_rollover_funded_total"] == 0
    assert outcome["workplace_rollover_unfilled_total"] == 80000
    assert outcome["first_unfilled_workplace_rollover"] == "2026-02-01"
    assert len(audit) == 1
    assert audit[0]["blocked_by_liquidity"]
