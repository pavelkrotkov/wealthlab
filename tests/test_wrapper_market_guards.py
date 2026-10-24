"""Unconfirmed return replacement and invented liquidity accounts cannot enter a run."""

import pytest

from tests.wrapper_market_cases import flat
from wealthlab.household.scenario import Scenario
from wealthlab.markets.household_run import run
from wealthlab.markets.paths import generate


@pytest.mark.parametrize(
    "updates, message",
    [
        (dict(replace_entered_returns_confirmed=False), "Confirm replacement"),
        (dict(factor="missing"), "Unknown account or factor"),
        (dict(account_id="missing"), "Unknown account or factor"),
    ],
)
def test_wrapper_mapping_is_explicit(updates, message):
    case, market, binding = flat()
    changed = binding.wrappers[0].model_copy(update=updates)
    binding = binding.model_copy(update=dict(wrappers=[changed, *binding.wrappers[1:]]))
    with pytest.raises(ValueError, match=message):
        run(case, generate(market), binding)


def test_an_unknown_liquidity_account_blocks_before_projection():
    case, market, binding = flat()
    data = case.model_dump(mode="json")
    data["ira_plan"]["liquidity_locks"] = [
        dict(
            id="bad_lock",
            provenance="assumption",
            account_id="missing",
            start="2026-01-01",
            end="2027-01-01",
        )
    ]
    with pytest.raises(ValueError, match="Unknown account"):
        run(Scenario.model_validate(data), generate(market), binding)
