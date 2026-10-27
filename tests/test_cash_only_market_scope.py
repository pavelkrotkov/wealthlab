"""A no-entry cash path is valid; latent unbound wealth or future funding is not."""

import pytest
from optimization_drilling_search_cases import case

from wealthlab.markets.household_run import run
from wealthlab.markets.paths import generate
from wealthlab.optimization.compile import compile_candidate


def inputs():
    profile = case()
    household, binding = compile_candidate(profile, [profile.dimensions[0].choices[-1]])
    return household, binding, generate(profile.training)


def test_nonzero_unbound_dormant_wealth_cannot_use_the_cash_only_exception():
    household, binding, batch = inputs()
    dormant = household.accounts[1].model_copy(update={"balance": 1})
    household = household.model_copy(update={"accounts": [household.accounts[0], dormant]})
    with pytest.raises(ValueError, match="Bind securities"):
        run(household, batch, binding)


def test_scheduled_contribution_cannot_fund_an_unbound_zero_account():
    from wealthlab.household.schedules import Contribution

    household, binding, batch = inputs()
    contribution = Contribution(
        id="later",
        provenance="illustration",
        destination="drilling",
        start=household.start,
        end=household.end,
        monthly_amount=100,
        currency="USD",
        annual_growth=0,
    )
    household = household.model_copy(update={"contributions": [contribution]})
    with pytest.raises(ValueError, match="Bind securities"):
        run(household, batch, binding)


def test_empty_market_binding_still_requires_cash_character_confirmation():
    household, binding, batch = inputs()
    binding = binding.model_copy(update={"ordinary_cash_character_confirmed": False})
    with pytest.raises(ValueError, match="Confirm ordinary yield"):
        run(household, batch, binding)
