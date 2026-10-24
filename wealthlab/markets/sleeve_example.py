"""Bind a synthetic household sleeve to the same paired long/short market factors."""

from wealthlab.markets.household_inputs import HouseholdBinding
from wealthlab.markets.inputs import MarketCase
from wealthlab.products.household_example import synthetic as household
from wealthlab.products.long_short_example import synthetic as economic


def synthetic(mode="deterministic", stress="early_crash"):
    data = economic(mode, stress)
    return (
        household(),
        MarketCase.model_validate(data["market"]),
        HouseholdBinding.model_validate(
            dict(
                sleeves=["sleeve"],
                replace_sleeve_observations_confirmed=True,
                cash_yield_timing="opening_value_received_before_month_end_sales",
                ordinary_cash_character_confirmed=True,
                other_accounts_unmodeled_returns_confirmed=True,
            )
        ),
    )
