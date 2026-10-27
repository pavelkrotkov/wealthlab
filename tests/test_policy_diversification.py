"""Actual trading costs explain flat-market policy differences without duplicated capital.

All choices begin with300000 and spend48000. Hold/saving pays2 commissions;
rebalancing plus two-way saving pays6; a bond completion purchase pays3.
The native tax-lot book carries original and purchased basis to actual exits.
"""

import pytest
from optimization_diversification_cases import case

from wealthlab.optimization.compile import compile_candidate
from wealthlab.optimization.inputs import PolicySearch
from wealthlab.optimization.search import search


@pytest.fixture(scope="module")
def result():
    return search(case())


def test_different_allocations_preserve_capital_and_pay_actual_trade_costs(result):
    assert result["selection"] == "candidate_0"
    assert [c["median_real_after_tax_exit_wealth"] for c in result["candidates"]] == [
        251998,
        251994,
        251997,
    ]
    assert result["held_out"]["assessment"]["eligible"]
    assert result["evaluated_candidates"] == 3


def test_allocation_controls_preserve_original_lots_accounts_and_income_inputs():
    baseline = case()
    candidate, _ = compile_candidate(baseline, [baseline.dimensions[-1].choices[1]])
    assert candidate.accounts == baseline.household.accounts
    assert candidate.lot_plan.case.lots == baseline.household.lot_plan.case.lots
    assert candidate.incomes == baseline.household.incomes
    assert candidate.tax_plan == baseline.household.tax_plan
    assert candidate.lot_plan.funding_sources == baseline.household.lot_plan.funding_sources


def test_balanced_choice_uses_sale_receipts_and_reports_remaining_drift():
    data = case().model_dump(mode="json")
    data["dimensions"][-1]["locked_choice"] = "balanced"
    result = search(PolicySearch.model_validate(data))
    audit = result["selected_training"]["details"][0]["rows"][-1]["lot_audit"]
    decision = audit["rebalance_decisions"][0]
    assert decision["gross_sales"] == 50000
    assert decision["gross_purchases"] == 49998
    assert decision["commissions"] == 2
    assert decision["residual_cash"] == 0
    assert decision["securities"][0]["weight_after"] != 0.5


def test_late_saving_after_complete_sale_reopens_assets_and_loses_exit_eligibility():
    data = case().model_dump(mode="json")
    for choice in data["dimensions"][-1]["choices"]:
        choice["savings"][0]["date"] = "2027-12-31"
    result = search(PolicySearch.model_validate(data))
    assert result["selection"] is None
    assert all(not c["constraints"]["completed_after_tax_exit"] for c in result["candidates"])
