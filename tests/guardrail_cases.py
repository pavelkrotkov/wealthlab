"""A large first-month loss is observed only before the second month's policy review."""

from tests.test_market_household_inflation import spending_case
from wealthlab.household.scenario import Scenario
from wealthlab.markets.guardrail_inputs import SpendingGuardrail
from wealthlab.markets.inputs import MarketCase


def plan():
    return SpendingGuardrail(
        expense_ids=["optional"],
        review_interval_months=1,
        trigger_real_wealth_drawdown=".20",
        restore_real_wealth_drawdown=".10",
        discretionary_cut_fraction=".20",
        spending_floor_fraction=".80",
        wealth_includes_spending_effects_confirmed=True,
    )


def case(recovery=False):
    household, market, binding = spending_case()
    data = household.model_dump(mode="json")
    data["expenses"].append(dict(data["expenses"][0], id="optional", category="discretionary"))
    data["lot_plan"]["funding_sources"][0]["commission"] = "0"
    paths = market.model_dump(mode="json")
    shocks = [dict(name="early loss", month=0, mark_shocks=dict(equities=-0.5))]
    if recovery:
        shocks.append(dict(name="following recovery", month=1, mark_shocks=dict(equities=1)))
    paths.update(mode="stress", shocks=shocks)
    return (
        Scenario.model_validate(data),
        MarketCase.model_validate(paths),
        binding.model_copy(update=dict(spending_guardrail=plan())),
    )
