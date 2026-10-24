"""Dated funding preserves capital and distinguishes beneficiary payments from parent cash.

A contribution request does not create a cash loan. Receipts received later in
the year cannot retroactively fund it. Reimbursements shift existing capital,
and the income deduction never appears as a deposit or assumed tax refund.
"""

from decimal import Decimal

from wealthlab.retirement.education import run
from wealthlab.retirement.education_example import synthetic
from wealthlab.retirement.education_inputs import EducationCase


def payload():
    return synthetic().model_dump(mode="json")


def calculate(data):
    return run(EducationCase.model_validate(data))


def test_funded_cash_and_external_payments_reconcile_without_a_tax_refund():
    result = run(synthetic())
    assert result["cash"] == 15000
    assert result["account_balances"] == {"college": 26200}
    assert result["contribution_basis"] == {"college": Decimal("18147.19")}
    assert result["external_disbursements"] == 5000
    assert result["cash"] + sum(result["account_balances"].values()) + 5000 == 42000 + 4200
    assert result["orders"][0]["unfunded"] == 3000
    assert result["orders"][0]["blocked_by_limit"] == 0


def test_later_cash_does_not_fund_an_earlier_contribution():
    data = payload()
    data["opening_cash"] = 0
    data["receipts"] = [dict(id="late", date="2026-12-01", amount=15000, provenance="illustration")]
    result = calculate(data)
    assert result["orders"][0]["funded"] == 0
    assert result["cash"] == 30000


def test_same_day_cash_funds_contribution_before_withdrawal():
    data = payload()
    data["opening_cash"] = 0
    data["receipts"] = [
        dict(id="same_day", date="2026-01-02", amount=15000, provenance="illustration")
    ]
    result = calculate(data)
    assert result["orders"][0]["funded"] == 15000
    assert result["cash"] == 15000
