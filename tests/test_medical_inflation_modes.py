"""All realized methods and strict selections use the same actual medical-bill ledger."""

import pytest

from wealthlab.markets.household_inputs import HouseholdBinding
from wealthlab.markets.household_run import run
from wealthlab.markets.medical_example import synthetic
from wealthlab.markets.paths import generate


@pytest.mark.parametrize("mode", ["deterministic", "historical", "monte_carlo", "stress"])
def test_each_realized_method_keeps_the_medical_cost_audit(mode):
    household, market, binding = synthetic(mode, "prolonged_inflation")
    result = run(household, generate(market), binding, [0])
    indexed = result["details"][0]["medical_bill_indexing"][0]
    assert indexed["realized_amount"] > 0
    assert result["indices"] == [0]
    assert result["household"]["hsa_plan"]["medical_bills"][0]["amount"] == "6000"


@pytest.mark.parametrize(
    "targets", [[dict(bill_id="unknown")], [dict(bill_id="care"), dict(bill_id="care")]]
)
def test_ambiguous_bill_bindings_fail_before_any_path(targets):
    household, market, binding = synthetic()
    data = binding.model_dump()
    data["medical_bill_inflation"] = [
        dict(t, amount_basis="projection_start_prices") for t in targets
    ]
    with pytest.raises(ValueError, match="unique existing bills"):
        run(household, generate(market), HouseholdBinding.model_validate(data))


def test_selected_bill_needs_an_explicit_start_price_basis():
    _, _, binding = synthetic()
    data = binding.model_dump()
    data["medical_bill_inflation"][0].pop("amount_basis")
    with pytest.raises(ValueError, match="amount_basis"):
        HouseholdBinding.model_validate(data)


def test_selected_bills_require_their_household_ledger():
    household, market, binding = synthetic()
    with pytest.raises(ValueError, match="explicit household HSA/bill plan"):
        run(household.model_copy(update=dict(hsa_plan=None)), generate(market), binding)


def test_near_zero_indexed_cost_cannot_silently_become_a_free_bill():
    household, market, binding = synthetic()
    market = market.model_copy(update=dict(expected_annual_inflation=-0.99999999))
    with pytest.raises(ValueError, match="round to zero"):
        run(household, generate(market), binding)
