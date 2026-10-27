"""Original source gains preserve independent bases and actual recognition timing.

The source10000value has1000federal/2000NJ basis. A denied federal contribution
recognizes its9000gain proportionally in2026; retained source sells in2027.
Direct sale realizes that gain immediately. The original lot commission is1.
Joint deductions/thresholds cover these small gains, leaving261999actual cash.
"""

import pytest
from optimization_cases import changed
from optimization_exchange_cases import case

from wealthlab.markets.paths import generate
from wealthlab.optimization.search import evaluate


def embedded():
    def edit(data):
        plans = [data["household"]["exchange_fund_plan"]]
        plans.extend(p["plan"] for p in data["exchange_opportunities"])
        for plan in plans:
            plan["source_lot"].update(federal_basis="1000", nj_basis="2000")
            plan["federal_contribution"] = "denied"

    return changed(case(), edit)


@pytest.mark.parametrize(
    "index,early,late", [(0, 0, 8999), (1, 4500, 4499), (2, 9000, -1), (3, 9000, -1)]
)
def test_earned_source_gain_moves_only_with_actual_contribution_or_sale(index, early, late):
    profile = embedded()
    selection = [profile.dimensions[0].choices[0], profile.dimensions[-1].choices[index]]
    candidate, result = evaluate(profile, selection, index, generate(profile.training))
    rows = result["details"][0]["rows"]
    assert rows[11]["annual_tax"]["federal"]["agi"] == early
    assert rows[-1]["annual_tax"]["federal"]["agi"] == late
    assert rows[-1]["closing_cash"] == 261999
    assert candidate["median_real_after_tax_exit_wealth"] == 261999
