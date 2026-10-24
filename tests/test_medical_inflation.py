"""Identical CPI paths can change spending feasibility without changing total wealth.

A 20% first-year inflation path makes a future USD6,000 bill cost USD7,200.
Keeping a nominal USD5,000 HSA cap leaves USD200 unpaid despite USD1,000 HSA
assets. Preserving the original bill share pays USD6,000 HSA plus USD1,200
cash. Both end at USD800, but only the latter funds every obligation.
"""

import pytest

from wealthlab.markets.household_compile import compile_marks
from wealthlab.markets.household_inputs import HouseholdBinding
from wealthlab.markets.household_run import paired, run
from wealthlab.markets.inputs import MarketCase
from wealthlab.markets.medical_example import synthetic
from wealthlab.markets.paths import generate


@pytest.fixture(scope="module")
def results():
    household, market, binding = synthetic()
    batch = generate(market)
    before = household.model_dump_json()
    left = run(household, batch, binding)
    data = binding.model_dump()
    data["medical_bill_inflation"][0]["hsa_election"] = "keep_bill_share"
    right = run(household, batch, HouseholdBinding.model_validate(data))
    assert household.model_dump_json() == before
    return left, right


def test_same_wealth_does_not_hide_different_spending_feasibility(results):
    left, right = results
    assert left["outcomes"][0]["funded"] is False
    assert right["outcomes"][0]["funded"] is True
    assert left["outcomes"][0]["ending_nominal_wealth"] == 800
    assert right["outcomes"][0]["ending_nominal_wealth"] == 800
    assert paired(left, right)[0]["shortfall_change"] == -200
    assert paired(left, right)[0]["real_wealth_change"] == 0


def test_audit_retains_entered_cost_and_actual_indexed_caps(results):
    left, right = results
    a = left["details"][0]["medical_bill_indexing"][0]
    b = right["details"][0]["medical_bill_indexing"][0]
    assert (a["input_amount"], a["realized_amount"]) == (6000, 7200)
    assert a["realized_hsa_cap"] == 5000
    assert b["realized_hsa_cap"] == 6000
    assert right["details"][0]["rows"][-1]["hsa_audit"]["receipt_remaining"] == {"care": 1200}


def test_due_month_inflation_does_not_change_an_already_due_bill():
    household, market, binding = synthetic()
    data = market.model_dump()
    data.update(
        mode="stress", shocks=[dict(name="Late inflation", month=12, inflation_override=0.5)]
    )
    batch = generate(MarketCase.model_validate(data))
    compiled = compile_marks(household, batch, binding, 0)
    assert compiled.hsa_plan.medical_bills[0].amount == 7200
    data["shocks"][0]["month"] = 11
    earlier = compile_marks(household, generate(MarketCase.model_validate(data)), binding, 0)
    assert earlier.hsa_plan.medical_bills[0].amount > 7200


def test_deflation_caps_a_nominal_hsa_election_at_the_actual_bill():
    household, market, binding = synthetic()
    market = market.model_copy(update=dict(expected_annual_inflation=-0.20))
    compiled = compile_marks(household, generate(market), binding, 0)
    assert compiled.hsa_plan.medical_bills[0].amount == 4800
    assert compiled.hsa_plan.medical_bills[0].hsa_amount == 4800
