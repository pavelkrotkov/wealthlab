"""All product books and new purchases share the same capital and actual source sale."""

from optimization_product_cases import case as product_case

from wealthlab.optimization.drilling_example import confirm_synthetic
from wealthlab.optimization.drilling_example import extend as with_drilling
from wealthlab.optimization.exchange_example import extend as with_exchange
from wealthlab.optimization.new_life_example import extend as with_life
from wealthlab.optimization.option_allocation_example import extend as with_options
from wealthlab.optimization.qoz_example import extend as with_qoz
from wealthlab.optimization.search import search


def test_qoz_and_native_products_compete_for_actual_shared_cash_without_duplicate_principal():
    profile = with_drilling(with_qoz(with_life(with_options(with_exchange(product_case())))))
    data = profile.model_dump(mode="json")
    locks = dict(
        retirement="early",
        exchange_contribution="all",
        new_policy_purchase="supplied_policy",
        drilling_participation="shares",
    )
    for dimension in data["dimensions"]:
        dimension["locked_choice"] = locks.get(dimension["id"])
    for market in (data["training"], data["validation"]):
        for asset in market["assets"]:
            asset.update(expected_annual_mark_return=0, annual_volatility=0, annual_cash_yield=0)
    result = search(confirm_synthetic(dict(data, drilling_envelope=None)))
    assert result["evaluated_candidates"] == 12
    assert all(
        c["opening_allocation_audit"]["allocated_opening_wealth"] == 340000
        for c in result["candidates"]
    )
    # Earlier zero-commission source sale replaces the one-dollar end-stock exit.
    assert result["held_out"]["assessment"]["median_real_after_tax_exit_wealth"] == 293092
    assert result["configured_validation_passed"]
