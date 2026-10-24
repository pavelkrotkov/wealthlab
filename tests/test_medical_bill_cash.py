"""A real bill reduces wealth once, even when HSA/cash cannot pay it at once.

The synthetic bill is USD6,000 against USD4,000 opening assets. A later
USD3,000 gift cures USD2,000 arrears without recurring reserve demand; a
USD5,000 employer HSA deposit later permits reimbursement of cash actually
paid. The final USD6,000 wealth follows external funding minus the bill.
"""

import pytest

from wealthlab.household.projection import project
from wealthlab.retirement.medical_bill_example import synthetic


@pytest.fixture(scope="module")
def rows():
    return project(synthetic())


def test_provider_payment_is_not_a_household_cash_receipt(rows):
    first = rows[0]
    assert first["medical_provider_paid"] == 3000
    assert first["medical_cash_paid"] == 1000
    assert first["healthcare"] == 4000
    assert first["tax_event_cash"] == 0
    assert first["hsa_withdrawal_cash"] == 0
    assert first["closing_cash"] == 0


def test_unpaid_bill_remains_a_real_liability(rows):
    assert rows[0]["medical_owed"] == 2000
    assert rows[0]["medical_bills_unfunded"] == 2000
    assert rows[0]["net_wealth"] == -2000
    assert rows[0]["funding_failure"]
    assert rows[1]["medical_owed"] == 0
    assert rows[1]["medical_arrears_paid"] == 2000
    assert rows[1]["reserve_target"] == 0


def test_actual_paid_receipt_cannot_be_reimbursed_twice_across_years(rows):
    assert sum(r["healthcare"] for r in rows) == 6000
    assert sum(r["hsa_withdrawal_cash"] for r in rows) == 3000
    assert rows[-1]["hsa_audit"]["receipt_remaining"] == {"care": 0}
    assert rows[14]["hsa_unfilled_requests"] == 3000
    assert rows[-1]["account_balances"] == dict(cash=4000, cash_hsa=2000)
    assert rows[-1]["net_wealth"] == 4000 + 3000 + 5000 - 6000
