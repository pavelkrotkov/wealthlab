"""An adjustable synthetic policy splits spending without changing its original total."""

from wealthlab.household.scenario import Scenario
from wealthlab.markets.household_inputs import HouseholdBinding


def enable(scenario, binding):
    data = scenario.model_dump(mode="json")
    expense = data["expenses"][0]
    expense["monthly_amount"] = "3000"
    discretionary = dict(
        expense, id="optional_spending", monthly_amount="2000", category="discretionary"
    )
    data["expenses"].append(discretionary)
    plan = binding.model_dump(mode="json")
    plan["spending_guardrail"] = dict(
        expense_ids=["optional_spending"],
        review_interval_months=1,
        trigger_real_wealth_drawdown=".20",
        restore_real_wealth_drawdown=".10",
        discretionary_cut_fraction=".20",
        spending_floor_fraction=".80",
        wealth_includes_spending_effects_confirmed=True,
    )
    return Scenario.model_validate(data), HouseholdBinding.model_validate(plan)
