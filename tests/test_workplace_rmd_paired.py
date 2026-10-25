"""A paired policy can change catch-up controls without changing any realized market paths."""

from wealthlab.household.scenario import Scenario
from wealthlab.markets.household_run import paired, run
from wealthlab.markets.paths import generate
from wealthlab.markets.workplace_rmd_example import synthetic


def test_optional_catchup_comparison_keeps_the_batch_and_exposes_requirement_failure():
    household, market, binding = synthetic()
    data = household.model_dump(mode="json")
    data["workplace_plan"]["cash_withdrawals"]["rmd"]["automatic_december_catchup"] = False
    alternate = Scenario.model_validate(data)
    batch = generate(market)
    baseline = run(household, batch, binding, [0])
    other = run(alternate, batch, binding, [0])
    differences = paired(baseline, other)
    assert baseline["batch_id"] == other["batch_id"]
    assert baseline["outcomes"][0]["funded"]
    assert not other["outcomes"][0]["funded"]
    assert other["outcomes"][0]["first_workplace_rmd_failure"] == "2026-12-01"
    assert differences[0]["funded_change"] == -1
