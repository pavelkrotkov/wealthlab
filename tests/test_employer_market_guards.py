"""Unconfirmed mappings and payout/tax conventions cannot become silent assumptions."""

import pytest
from employer_market_cases import flat

from wealthlab.markets.household_run import run
from wealthlab.markets.inputs import MarketCase
from wealthlab.markets.paths import generate


@pytest.mark.parametrize(
    ("field", "value", "message"),
    [
        ("account_id", "missing", "existing compensation account"),
        ("factor", "missing", "Unknown employer market factor"),
        ("replace_entered_net_returns_confirmed", False, "Confirm replacement"),
    ],
)
def test_invalid_employer_binding_blocks_before_execution(field, value, message):
    household, market, binding = flat()
    data = binding.model_dump(mode="json")
    data["employers"][0][field] = value
    with pytest.raises(ValueError, match=message):
        run(household, generate(market), type(binding).model_validate(data))


@pytest.mark.parametrize("mutation", ["cash_yield", "role", "confirmation", "owner"])
def test_tax_yield_and_work_link_require_explicit_valid_scope(mutation):
    household, market, binding = flat()
    terms, data = market.model_dump(mode="json"), binding.model_dump(mode="json")
    if mutation == "cash_yield":
        terms["assets"][0]["annual_cash_yield"] = 0.01
    elif mutation == "role":
        terms["assets"][0]["role"] = "equity"
    elif mutation == "confirmation":
        data["employers"][0]["employment"]["replace_future_work_changes_confirmed"] = False
    else:
        data["employers"][0]["employment"]["path_id"] = "missing"
    with pytest.raises(ValueError):
        run(
            household,
            generate(MarketCase.model_validate(terms)),
            type(binding).model_validate(data),
        )
