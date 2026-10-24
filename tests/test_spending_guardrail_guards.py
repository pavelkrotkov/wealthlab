"""The spending floor and essential budgets cannot be silently weakened by the policy."""

import pytest

from tests.guardrail_cases import case, plan
from wealthlab.markets.guardrail_inputs import SpendingGuardrail
from wealthlab.markets.household_run import run
from wealthlab.markets.paths import generate


@pytest.mark.parametrize(
    "updates, message",
    [
        (dict(discretionary_cut_fraction=".3"), "spending floor"),
        (dict(restore_real_wealth_drawdown=".3"), "below the cut trigger"),
        (dict(expense_ids=["optional", "optional"]), "must be unique"),
    ],
)
def test_guardrail_contract_bounds(updates, message):
    with pytest.raises(ValueError, match=message):
        SpendingGuardrail.model_validate(dict(plan().model_dump(), **updates))


@pytest.mark.parametrize(
    "updates, message",
    [
        (dict(expense_ids=["living"]), "only explicitly selected discretionary"),
        (dict(expense_ids=["missing"]), "Unknown guardrail expense"),
        (dict(wealth_includes_spending_effects_confirmed=False), "Confirm that guardrail"),
    ],
)
def test_guardrail_household_scope(updates, message):
    household, market, binding = case()
    altered = binding.spending_guardrail.model_copy(update=updates)
    with pytest.raises(ValueError, match=message):
        run(
            household, generate(market), binding.model_copy(update=dict(spending_guardrail=altered))
        )


def test_drawdown_reference_requires_positive_opening_net_wealth():
    from wealthlab.household.scenario import Scenario

    household, market, binding = case()
    data = household.model_dump(mode="json")
    data["debts"] = [
        dict(
            id="debt",
            provenance="illustration",
            currency="USD",
            balance="200000",
            annual_rate=0,
            monthly_payment="1000",
        )
    ]
    with pytest.raises(ValueError, match="positive opening net wealth"):
        run(Scenario.model_validate(data), generate(market), binding)
