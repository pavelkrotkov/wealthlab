"""Allowed schedule edits preserve independent opening capital and tax facts."""

import pytest
from optimization_cases import flat

from wealthlab.optimization.compile import compile_candidate
from wealthlab.optimization.inputs import PolicyChoice
from wealthlab.products.option_household_example import synthetic as options


def test_retirement_and_funding_order_preserve_baseline_capital_and_tax_inputs():
    case = flat()
    choice = PolicyChoice(
        id="choice",
        retirement_dates={"person_a": "2026-07-01"},
        lot_funding_order=[0],
        harvest_policies=[],
    )
    candidate, _ = compile_candidate(case, [choice])
    assert candidate.accounts == case.household.accounts
    assert candidate.tax_plan == case.household.tax_plan
    assert candidate.expenses == case.household.expenses
    assert str(candidate.members[0].retirement_date) == "2026-07-01"
    assert str(case.household.members[0].retirement_date) == "2027-01-01"


@pytest.mark.parametrize("order", [[], [0, 0], [1]])
def test_funding_order_cannot_add_remove_or_duplicate_sale_permissions(order):
    with pytest.raises(ValueError, match="permutation"):
        compile_candidate(flat(), [PolicyChoice(id="choice", lot_funding_order=order)])


def test_missing_ira_plan_cannot_make_a_conversion_tax_free():
    with pytest.raises(ValueError, match="existing configured IRA"):
        compile_candidate(flat(), [PolicyChoice(id="choice", ira_orders=[])])


def test_options_require_their_own_native_market_binding():
    case = flat().model_copy(update=dict(household=options()))
    with pytest.raises(ValueError, match="native stock/index market binding"):
        compile_candidate(case, [])


def test_guardrail_choice_can_explicitly_restore_fixed_spending():
    case = flat()
    choice = PolicyChoice(id="fixed", change_guardrail=True, guardrail=None)
    candidate, binding = compile_candidate(case, [choice])
    assert binding.spending_guardrail is None
    assert candidate.expenses == case.household.expenses
