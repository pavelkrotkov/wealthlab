"""Cash-basis deductions conserve money and keep later tax recoveries explicit."""

from datetime import date
from decimal import Decimal as D

import pytest

from wealthlab.household.projection import project
from wealthlab.tax.annual import evaluate
from wealthlab.tax.facts import FederalIncome
from wealthlab.tax.nj_facts import NJIncome
from wealthlab.tax.projection_inputs import TaxEvent


def test_paid_state_tax_couples_once_and_entered_mode_remains_explicit(itemizer):
    """Opening cash already includes $1,000 paid; only the remaining NJ tax leaves cash.

    The deduction nevertheless includes both payments in their calendar year.
    """
    household = itemizer(nj_paid="1000")
    row = project(household)[0]
    tax = row["annual_tax"]
    assert tax["state_income_tax_deduction_input"] == D("8570.10")
    assert tax["federal"]["itemized_deduction"] == D("38570.10")
    # The opening $1,000 is already reflected in starting cash, not paid again.
    assert row["tax_settlement_paid"] == tax["federal"]["income_tax"] + D("7570.10")
    plan = household.tax_plan.model_copy(update={"state_deduction_mode": "entered"})
    entered = project(household.model_copy(update={"tax_plan": plan}))[0]["annual_tax"]
    assert entered["state_income_tax_deduction_input"] == 0
    assert entered["federal"]["income_tax"] == evaluate(plan.cases[0])["federal"]["income_tax"]
    assert tax["federal"]["income_tax"] < entered["federal"]["income_tax"]


def test_unpaid_state_tax_is_deducted_only_when_later_paid(itemizer):
    household = itemizer(cash="1000", end="2027-02-01")
    event = TaxEvent(
        date=date(2027, 1, 1),
        description="Explicit nontaxable cash receipt",
        cash_received=D(50000),
        federal=FederalIncome(),
        new_jersey=NJIncome(),
    )
    plan = household.tax_plan.model_copy(update={"events": [event]})
    december, january = project(household.model_copy(update={"tax_plan": plan}))
    assert december["annual_tax"]["state_income_tax_deduction_input"] == 1000
    assert january["annual_tax"]["state_income_tax_deduction_input"] == D("7570.10")
    assert january["prior_tax_paid"] == december["tax_owed"]
    assert january["tax_owed"] == 0


def test_beneficial_refund_requires_assumption_and_recognizes_only_on_receipt(itemizer):
    household = itemizer(end="2027-05-01", nj_paid="10000")
    with pytest.raises(ValueError, match="state_refund_taxable_fractions"):
        project(household)
    plan = household.tax_plan.model_copy(update={"state_refund_taxable_fractions": {2026: D(1)}})
    rows = project(household.model_copy(update={"tax_plan": plan}))
    assert rows[0]["annual_tax"]["state_refund_taxable"] == D("1429.90")
    assert rows[3]["taxable_state_refund"] == 0
    assert rows[4]["taxable_state_refund"] == D("1429.90")
    assert rows[4]["annual_tax"]["federal"]["agi"] == D("1429.90")
    assert rows[4]["annual_tax"]["new_jersey"]["income_tax"] == 0


def test_capped_salt_refund_without_benefit_needs_no_fraction(itemizer):
    household = itemizer(nj_paid="10000")
    plan = household.tax_plan
    case = plan.cases[0]
    deductions = case.federal_deductions.model_copy(update={"property_tax_paid": D(40000)})
    case = case.model_copy(update={"federal_deductions": deductions})
    row = project(
        household.model_copy(update={"tax_plan": plan.model_copy(update={"cases": [case]})})
    )[0]
    assert row["annual_tax"]["state_refund_taxable"] == 0
    assert row["annual_tax"]["state_refund_treatment"] == "Recomputed prior federal tax unchanged"
