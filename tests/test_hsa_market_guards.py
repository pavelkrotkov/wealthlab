"""No missing path exposure, unconfirmed replacement or unsupported execution prices."""

import pytest

from wealthlab.markets.household_validation import validate
from wealthlab.markets.hsa_example import synthetic
from wealthlab.markets.paths import generate


@pytest.mark.parametrize(
    "change, message",
    [
        (dict(replace_hsa_observations_confirmed=False), "Confirm replacement"),
        (dict(hsa_securities=[]), "every invested HSA security"),
    ],
)
def test_incomplete_binding_cannot_run_as_an_hsa_market_projection(change, message):
    household, market, binding = synthetic()
    with pytest.raises(ValueError, match=message):
        validate(household, generate(market), binding.model_copy(update=change), 0)


def test_total_return_marks_cannot_become_price_plus_cash_hsa_income():
    household, market, binding = synthetic()
    asset = market.assets[0].model_copy(update=dict(annual_cash_yield=0))
    market = market.model_copy(
        update=dict(assets=[asset], return_convention="total_return_reinvested")
    )
    with pytest.raises(ValueError, match="separate price returns"):
        validate(household, generate(market), binding, 0)


def test_entered_hsa_trade_cannot_use_an_old_fixed_price_in_simulated_markets():
    from wealthlab.retirement.hsa_investment_example import synthetic as book

    household, market, binding = synthetic()
    case = household.hsa_plan.investments.case.model_copy(update=dict(trades=book().case.trades))
    investments = household.hsa_plan.investments.model_copy(update=dict(case=case))
    household = household.model_copy(
        update=dict(hsa_plan=household.hsa_plan.model_copy(update=dict(investments=investments)))
    )
    with pytest.raises(ValueError, match="execution-price adapter"):
        validate(household, generate(market), binding, 0)
