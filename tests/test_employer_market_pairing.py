"""Prefix-observed triggers preserve paired, reproducible policy comparisons."""

from decimal import Decimal

from employer_market_cases import crashed

from wealthlab.markets.household_compile import compile_marks
from wealthlab.markets.household_run import paired, run
from wealthlab.markets.inputs import MarketCase
from wealthlab.markets.paths import generate


def test_same_prefix_gives_same_work_changes_despite_different_future_returns():
    household, batch, binding = crashed()
    earlier = compile_marks(household, batch, binding, 0)
    terms = dict(batch.metadata["input"])
    terms["shocks"] = [
        *terms["shocks"],
        dict(name="later", month=8, mark_shocks=dict(employer=0.1)),
    ]
    later = compile_marks(household, generate(MarketCase.model_validate(terms)), binding, 0)
    assert earlier.employment_plan == later.employment_plan
    assert household.employment_plan.paths[0].changes == []


def test_paired_retention_policy_changes_forfeiture_without_inventing_wages():
    household, batch, binding = crashed()
    data = binding.model_dump(mode="json")
    data["employers"][0]["employment"]["forfeit_remaining_unvested"] = False
    other = type(binding).model_validate(data)
    left, right = run(household, batch, binding), run(household, batch, other)
    assert paired(left, right)[0]["real_wealth_change"] == 0
    assert right["details"][0]["rows"][-1]["employer_unvested_contingent"] == Decimal(40000)
