"""Actual participation shares the original wallet with all other native product choices."""

from optimization_product_cases import case as product_case

from wealthlab.optimization.drilling_example import confirm_synthetic
from wealthlab.optimization.drilling_example import extend as with_drilling
from wealthlab.optimization.new_life_example import extend as with_new_life
from wealthlab.optimization.option_allocation_example import extend as with_options
from wealthlab.optimization.search import search


def test_conditional_participation_and_new_purchases_preserve_the_same_household_capital():
    profile = with_drilling(with_new_life(with_options(product_case())))
    data = profile.model_dump(mode="json")
    data["dimensions"][0]["locked_choice"] = "early"
    data["targets"]["maximum_issuer_weight"] = None
    for market in (data["training"], data["validation"]):
        for asset in market["assets"]:
            asset.update(expected_annual_mark_return=0, annual_volatility=0)
    result = search(confirm_synthetic(dict(data, drilling_envelope=None)))
    assert result["evaluated_candidates"] == 18
    assert all(
        c["opening_allocation_audit"]["allocated_opening_wealth"] == 340000
        for c in result["candidates"]
    )
    assert result["held_out"]["assessment"]["median_real_after_tax_exit_wealth"] == 293091
    assert result["configured_validation_passed"]
    assert result["held_out"]["results"]["details"][0]["rows"][-1]["closing_cash"] == 293091
