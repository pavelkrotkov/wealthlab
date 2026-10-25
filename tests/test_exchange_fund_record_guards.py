"""Date axes, source identities and independent basket allocations must be complete."""

import pytest
from exchange_fund_cases import change, flat

from wealthlab.products.exchange_fund_household import Ledger


@pytest.mark.parametrize("field", ["value_weight", "federal_basis_weight", "nj_basis_weight"])
def test_each_independent_basket_allocation_must_sum_to_one(field):
    with pytest.raises(ValueError, match="sum to one"):
        Ledger(
            change(flat(), lambda d: d["exchange_fund_plan"]["basket"][0].update({field: "0.4"}))
        )


@pytest.mark.parametrize(
    "mutation,message",
    [
        (lambda p: p["observations"].pop(), "cover all"),
        (lambda p: p["observations"][0].update(provenance="unresolved"), "Resolve"),
        (lambda p: p["observations"][0].update(id="original_lot"), "unique"),
        (lambda p: p["observations"][0]["prices"].pop("original"), "every original"),
        (lambda p: p["requests"][0].update(date="2026-12-30"), "month-end"),
        (lambda p: p["requests"][0]["early_tax"].update(date="2026-12-30"), "tax date"),
        (lambda p: p["basket"][0]["security"].update(provenance="unresolved"), "Resolve"),
        (lambda p: p["basket"][0]["security"].update(kind="collectible"), "stock/ETF"),
    ],
)
def test_incomplete_or_unresolved_source_blocks(mutation, message):
    def configure(data):
        mutation(data["exchange_fund_plan"])

    with pytest.raises(ValueError, match=message):
        Ledger(change(flat(), configure))


def test_distributions_above_supplied_basis_or_nav_block_before_money_is_invented():
    from wealthlab.household.projection import project

    def configure(data):
        data["exchange_fund_plan"]["observations"][0]["distribution"] = "21000"

    with pytest.raises(ValueError, match="exceeds NAV or supplied"):
        project(change(flat(), configure))
