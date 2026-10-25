"""Gross receipts, net liquidity and source-paid tax must reconcile independently.

A pension is not payroll, and return of basis is not taxable pension income.
The recipient cannot redirect cash already remitted by its payer to fund an HSA.
"""

from decimal import Decimal

import pytest
from pydantic import ValidationError

from wealthlab.tax.recognition import event
from wealthlab.tax.source_example import pension, synthetic


@pytest.mark.parametrize("net,federal,nj", [(8001, 2000, 0), (0, 10001, 0), (0, 0, 10001)])
def test_reject_cash_or_withholding_that_does_not_reconcile(net, federal, nj):
    data = pension().model_dump(mode="json")
    data.update(
        cash_received=net,
        withholding=dict(gross_cash=10000, federal_income_withheld=federal, nj_withheld=nj),
    )
    with pytest.raises(ValidationError, match="reconcile"):
        type(pension()).model_validate(data)


def test_credit_source_payments_without_reducing_gross_taxable_income():
    case = synthetic().tax_plan.cases[0]
    after = event(case, pension(), "actual_payments")
    assert after.federal_income.taxable_pension == 10000
    assert after.payments.federal_income_withheld == 2000
    assert case.payments.federal_income_withheld == 0


@pytest.mark.parametrize("mode,deduction", [("actual_payments", 300), ("entered", 0)])
def test_only_actual_payment_mode_adds_nj_source_tax_to_state_deduction(mode, deduction):
    data = pension().model_dump(mode="json")
    data["withholding"].update(nj_withheld=300)
    data["cash_received"] = 7700
    item = type(pension()).model_validate(data)
    case = synthetic().tax_plan.cases[0]
    after = event(case, item, mode)
    assert after.payments.nj_withheld == 300
    assert after.federal_deductions.state_local_income_tax_paid == deduction
    assert after.payments.federal_income_withheld == 2000


def test_gross_distribution_can_include_untaxed_return_of_basis():
    item = pension().model_copy(
        update=dict(
            federal=pension().federal.model_copy(update=dict(taxable_pension=Decimal(6000)))
        )
    )
    after = event(synthetic().tax_plan.cases[0], item)
    assert item.cash_received == 8000
    assert after.federal_income.taxable_pension == 6000
    assert after.payments.federal_income_withheld == 2000
