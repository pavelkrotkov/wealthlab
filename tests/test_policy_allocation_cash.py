"""Product mixes change allocation and native costs, never household starting capital.

Flat zero-cost investments return only their original principal. With130/30
notionals and10bps entry plus exit, a20000allocation has32000gross exposure
and pays32at each end, reducing ending cash by64. A private cash exit recovers
its paid20000basis and recognizes its actual64loss without adding a tax refund.
"""

import pytest
from optimization_allocation_cases import case
from optimization_cases import changed

from wealthlab.optimization.search import search


@pytest.fixture(scope="module")
def result():
    return search(case())


def test_cash_margin_private_and_blended_policies_have_identical_original_capital(result):
    assert [c["median_real_after_tax_exit_wealth"] for c in result["candidates"]] == [251999] * 4
    assert result["held_out"]["assessment"]["eligible"]
    audits = [c["opening_allocation_audit"] for c in result["candidates"]]
    assert all(
        a["original_opening_wealth"] == a["allocated_opening_wealth"] == 300000 for a in audits
    )
    assert [a["cash_debits"]["cash"] for a in audits] == [0, 20000, 20000, 20000]
    assert audits[3]["new_sleeve_capital"] == dict(new_margin=10000, new_private=10000)


def test_native_entry_and_exit_costs_reduce_wealth_once_for_every_nonzero_mix():
    def edit(data):
        for opportunity in data["sleeve_opportunities"]:
            opportunity["unit"]["case"].update(turnover_cost=".001", exit_cost=".001")

    result = search(changed(case(), edit))
    assert [c["median_real_after_tax_exit_wealth"] for c in result["candidates"]] == [
        251999,
        251935,
        251935,
        251935,
    ]
    assert result["selection"] == "candidate_0"
    assert all(c["median_net_cash_tax"] == 0 for c in result["candidates"])


def test_insufficient_combined_cash_marks_the_mix_unsupported_without_changing_other_candidates():
    result = search(
        changed(case(), lambda d: d["household"]["accounts"][0].update(balance="15000"))
    )
    assert result["evaluated_candidates"] == 4
    assert all("available source cash" in c["unsupported_reason"] for c in result["candidates"][1:])
    # Seven full months of cash, then sixteen funding sales and one terminal sale:
    # 115000capital -48000spending -17actual one-dollar commissions.
    assert result["candidates"][0]["median_marked_real_wealth"] == 66983
