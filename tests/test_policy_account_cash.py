"""Existing books execute distributions once; tuition remains an actual spending bill.

Opening assets326000 minus48000living,6000tuition,1sale commission and1000
age-based workplace additional tax leaves270999. HSA reimbursements recover
prior paid receipts, not a new expense; source withholding is a tax payment.
"""

import pytest
from optimization_account_cases import case

from wealthlab.optimization.search import search


@pytest.fixture(scope="module")
def result():
    return search(case())


def test_native_workplace_hsa_education_exit_conserves_household_capital(result):
    assert result["selection"] == "candidate_0"
    assert [c["median_real_after_tax_exit_wealth"] for c in result["candidates"]] == [
        270999,
        270999,
    ]
    assert result["held_out"]["assessment"]["eligible"]


def test_source_withholding_and_prior_paid_receipts_remain_separate_from_spending(result):
    rows = result["selected_training"]["details"][0]["rows"]
    assert sum(r["education_wrapper_paid"] for r in rows) == 6000
    assert sum(r["hsa_withdrawal_cash"] for r in rows) == 10000
    assert sum(r["workplace_withdrawal_gross"] for r in rows) == 10000
    assert sum(r["workplace_withdrawal_net"] for r in rows) == 8000
    assert rows[-1]["hsa_audit"]["receipt_remaining"]["past_medical"] == 2000
    assert rows[-1]["education_audit"]["years"][-1]["contribution_basis"]["college"] == 0


def test_partial_schedule_preserves_assets_and_prevents_completed_exit_ranking():
    data = case().model_dump(mode="json")
    for choice in data["dimensions"][-1]["choices"]:
        choice["workplace_cash_orders"][0]["amount"] = "5000"
    result = search(type(case()).model_validate(data))
    assert result["selection"] is None
    assert all(c["median_real_after_tax_exit_wealth"] is None for c in result["candidates"])
    assert all(not c["constraints"]["completed_after_tax_exit"] for c in result["candidates"])


def test_wrapper_proxy_does_not_silently_certify_underlying_issuer_inventory():
    data = case().model_dump(mode="json")
    data["targets"]["maximum_issuer_weight"] = "1"
    result = search(type(case()).model_validate(data))
    assert result["selection"] is None
    assert all(not c["constraints"]["issuer_limit"] for c in result["candidates"])
