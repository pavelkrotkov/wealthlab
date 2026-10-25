"""Monthly returns cannot supply intramonth quotes, roll prices or settlement liquidity."""

import pytest

from tests.option_market_cases import change, flat
from wealthlab.markets.household_inputs import HouseholdBinding
from wealthlab.markets.household_run import run


@pytest.mark.parametrize(
    "field", ["replace_dated_marks_confirmed", "hypothetical_model_execution_confirmed"]
)
def test_unconfirmed_replacement_or_model_execution_is_blocked(field):
    scenario, batch, binding = flat()
    data = binding.model_dump(mode="json")
    data["options"][field] = False
    with pytest.raises(ValueError, match="Confirm replacement"):
        run(scenario, batch, HouseholdBinding.model_validate(data))


@pytest.mark.parametrize(
    "field,value,message",
    [
        ("stock_factor", "unknown", "two distinct known"),
        ("index_factor", "stock", "two distinct known"),
        ("account_id", "missing", "complete actual"),
    ],
)
def test_unknown_or_duplicate_option_bindings_are_rejected(field, value, message):
    scenario, batch, binding = flat()
    data = binding.model_dump(mode="json")
    data["options"][field] = value
    with pytest.raises(ValueError, match=message):
        run(scenario, batch, HouseholdBinding.model_validate(data))


def test_intramonth_expiry_and_reused_closing_quotes_are_rejected():
    scenario, batch, binding = flat()
    bad = change(
        scenario, lambda data: data["option_plan"]["case"]["legs"][0].update(expiry="2026-02-15")
    )
    with pytest.raises(ValueError, match="Intramonth option expiry"):
        run(bad, batch, binding)
    bad = change(
        scenario,
        lambda data: data["option_plan"]["case"].update(
            events=[dict(leg_id="stock_call", date="2026-01-31", action="close", close_price="1")]
        ),
    )
    with pytest.raises(ValueError, match="close quotes cannot be reused"):
        run(bad, batch, binding)
