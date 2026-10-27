"""Whole new policies share capital with cash options and four existing product books.

The original340000 includes all existing positions exactly once. Option units
add496net each and the complete new policy returns100above its2000premiums.
The best supplied flat choice therefore closes at291999+992+100=293091cash.

Source quotes and funds remain synthetic; the test verifies actual execution
rather than treating illustrated values or premium spending as starting wealth.
"""

from optimization_product_cases import case as product_case

from wealthlab.optimization.exchange_example import extend as with_exchange
from wealthlab.optimization.inputs import PolicySearch
from wealthlab.optimization.new_life_example import extend as with_life
from wealthlab.optimization.option_allocation_example import extend as with_options
from wealthlab.optimization.search import search


def test_whole_new_policy_compounds_with_other_products_without_extra_opening_capital():
    data = with_life(with_options(with_exchange(product_case()))).model_dump(mode="json")
    for market in (data["training"], data["validation"]):
        for asset in market["assets"]:
            asset.update(expected_annual_mark_return=0, annual_volatility=0, annual_cash_yield=0)
    result = search(PolicySearch.model_validate(data))
    candidates = result["candidates"]
    assert len(candidates) == 24 and all(c["eligible"] for c in candidates)
    assert {c["opening_allocation_audit"]["allocated_opening_wealth"] for c in candidates} == {
        340000
    }
    assert result["held_out"]["assessment"]["median_real_after_tax_exit_wealth"] == 293091
