"""Unknown eligibility envelopes, missing factors and unsupported cash/locks fail closed."""

import pytest
from drilling_market_cases import edited

from wealthlab.markets.household_run import run
from wealthlab.markets.paths import generate


@pytest.mark.parametrize(
    ("field", "value", "message"),
    [
        ("account_id", "unknown", "actual drilling account"),
        ("commodity_factor", "unknown", "known commodity/reference"),
        ("reference_factor", "commodity", "distinct"),
        ("replace_price_observations_confirmed", False, "Confirm replacement"),
        (
            "fixed_production_cost_tax_and_property_exit_quotes_valid_for_prices_confirmed",
            False,
            "validity",
        ),
    ],
)
def test_unconfirmed_binding_terms_never_run_an_actual_projection(field, value, message):
    case = edited(lambda data: data["binding"]["drilling"].update({field: value}))
    with pytest.raises(ValueError, match=message):
        run(case.household, generate(case.market), case.binding)


@pytest.mark.parametrize(
    ("change", "message"),
    [
        ("yield", "cash yields"),
        ("commodity_lock", "Locked commodity"),
        ("zero_reference", "Nonpositive reference"),
        ("horizon", "every household month"),
        ("missing_binding", "actual drilling account"),
        ("missing_month", "observations must cover"),
    ],
)
def test_unsupported_factor_cash_lock_price_and_horizon_are_rejected(change, message):
    def configure(data):
        if change == "yield":
            data["market"]["assets"][0]["annual_cash_yield"] = 0.01
        if change == "commodity_lock":
            data["market"]["shocks"][0]["lock_months"] = {"commodity": 1}
        if change == "zero_reference":
            data["market"]["shocks"][1]["mark_shocks"]["reference"] = -1
        if change == "horizon":
            data["market"]["end"] = "2026-04-01"
        if change == "missing_month":
            data["household"]["drilling_plan"]["observations"].pop()
        if change == "missing_binding":
            data["binding"]["drilling"] = None

    case = edited(configure)
    with pytest.raises(ValueError, match=message):
        run(case.household, generate(case.market), case.binding)
