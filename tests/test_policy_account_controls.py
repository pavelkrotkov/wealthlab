"""Account controls cannot edit historical cost, benefits or tax qualification.

Atomic schedules preserve source plans while native adapters still validate
eligibility and actual cash. Dimensions own each schedule independently;
conflicting writers and malformed inactive choices cannot be hidden by locks.
"""

import pytest
from optimization_account_cases import case
from optimization_cases import flat

from wealthlab.optimization.account_controls import AccountControls
from wealthlab.optimization.compile import compile_candidate
from wealthlab.optimization.inputs import PolicyChoice, PolicySearch
from wealthlab.optimization.validation import validate


@pytest.mark.parametrize("field", AccountControls.model_fields)
def test_schedule_choice_requires_a_configured_native_account_plan(field):
    with pytest.raises(ValueError, match="existing configured"):
        compile_candidate(flat(), [PolicyChoice.model_validate(dict(id="choice", **{field: []}))])


def test_schedule_choices_preserve_opening_capital_basis_spending_and_eligibility():
    baseline = case()
    choice = baseline.dimensions[-1].choices[-1]
    candidate, _ = compile_candidate(baseline, [choice])
    assert candidate.accounts == baseline.household.accounts
    assert candidate.expenses == baseline.household.expenses
    assert candidate.tax_plan == baseline.household.tax_plan
    assert candidate.education_plan == baseline.household.education_plan
    assert candidate.workplace_plan.years == baseline.household.workplace_plan.years
    assert candidate.hsa_plan.years == baseline.household.hsa_plan.years
    assert candidate.hsa_plan.medical_receipts == baseline.household.hsa_plan.medical_receipts


@pytest.mark.parametrize(
    "edit", [dict(id="invented"), dict(mode="allow_nonqualified"), dict(receipt_ids=[])]
)
def test_hsa_choice_cannot_change_receipt_eligibility_or_tax_identity(edit):
    baseline = case()
    order = baseline.household.hsa_plan.withdrawals[0].model_dump(mode="json")
    choice = PolicyChoice.model_validate(dict(id="choice", hsa_withdrawals=[dict(order, **edit)]))
    with pytest.raises(ValueError, match="only existing withdrawal dates and amounts"):
        compile_candidate(baseline, [choice])


def test_hsa_personal_schedule_cannot_manufacture_employer_compensation():
    order = dict(
        id="new_benefit",
        provenance="illustration",
        date="2026-01-01",
        destination="cash_hsa",
        source="direct_employer",
        amount="1000",
    )
    choice = PolicyChoice.model_validate(dict(id="choice", hsa_personal_contributions=[order]))
    with pytest.raises(ValueError, match="cannot change employer funding"):
        compile_candidate(case(), [choice])


def test_two_dimensions_cannot_overwrite_the_same_account_election():
    data = case().model_dump(mode="json")
    data["dimensions"].append(dict(id="duplicate", choices=[dict(id="clear", hsa_withdrawals=[])]))
    with pytest.raises(ValueError, match="cannot write the same"):
        validate(PolicySearch.model_validate(data))


def test_clearing_hsa_orders_preserves_only_still_applicable_tax_assumptions():
    data = case().model_dump(mode="json")
    plan = data["household"]["hsa_plan"]
    identity = plan["withdrawals"][0]["id"]
    plan["nj_withdrawal_taxable_fractions"] = {identity: "0.5"}
    plan["generated_distribution_tax_excluded_from_other_inputs_confirmed"] = True
    baseline = PolicySearch.model_validate(data)
    candidate, _ = compile_candidate(baseline, [PolicyChoice(id="clear", hsa_withdrawals=[])])
    assert candidate.hsa_plan.withdrawals == []
    assert candidate.hsa_plan.nj_withdrawal_taxable_fractions == {}
    assert baseline.household.hsa_plan is not None
    assert baseline.household.hsa_plan.nj_withdrawal_taxable_fractions[identity] == 0.5


@pytest.mark.parametrize("plan", ["hsa_plan", "education_plan"])
def test_wrapper_accounts_require_their_native_cash_and_tax_book(plan):
    data = case().model_dump(mode="json")
    data["household"][plan] = None
    with pytest.raises(ValueError, match="accounts require a configured"):
        compile_candidate(PolicySearch.model_validate(data), [])
