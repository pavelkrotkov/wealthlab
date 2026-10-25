"""New cash options and exchange splits compose with three other native product books.

The original340000capital buys no extra source stock. Existing products return
principal once; each actually purchased option unit contributes its496net gain.
"""

import pytest
from optimization_cases import changed
from optimization_product_cases import case as product_case

from wealthlab.optimization.exchange_example import extend
from wealthlab.optimization.inputs import PolicySearch
from wealthlab.optimization.option_allocation_example import extend as with_options
from wealthlab.optimization.search import search


def test_exchange_choices_and_new_options_share_the_original_product_capital():
    data = with_options(extend(product_case())).model_dump(mode="json")
    for market in (data["training"], data["validation"]):
        for asset in market["assets"]:
            asset.update(expected_annual_mark_return=0, annual_volatility=0, annual_cash_yield=0)
    result = search(PolicySearch.model_validate(data))
    candidates = result["candidates"]
    assert len(candidates) == 12 and all(c["eligible"] for c in candidates)
    assert sorted({c["median_real_after_tax_exit_wealth"] for c in candidates}) == [
        291999,
        292495,
        292991,
    ]
    assert all(
        c["opening_allocation_audit"]["allocated_opening_wealth"] == 340000 for c in candidates
    )
    assert result["held_out"]["assessment"]["median_real_after_tax_exit_wealth"] == 292991


def test_synthetic_exchange_menu_cannot_replace_user_offers_or_invent_private_positions():
    from optimization_exchange_cases import case

    with pytest.raises(ValueError, match="replace existing"):
        extend(case())
    private = changed(product_case(), lambda d: d["household"].update(synthetic=False))
    with pytest.raises(ValueError, match="only extends synthetic"):
        extend(private)


def test_nonzero_supplied_flows_need_complete_entered_profiles_instead_of_scaling():
    def edit(data):
        data["household"]["exchange_fund_plan"]["observations"][0]["distribution"] = "100"

    with pytest.raises(ValueError, match="complete supplied offers"):
        extend(changed(product_case(), edit))
