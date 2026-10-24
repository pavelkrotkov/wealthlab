"""A revised NJ refund cannot silently acquire tax-free federal treatment."""

from datetime import date

import pytest

from tests.return_reconciliation_cases import allowed_loss, close_december
from tests.test_closed_return_positions import advance
from wealthlab.tax.return_reconciliation import revise


def test_unknown_tax_benefit_recovery_blocks_before_mutating_return_positions():
    taxes, wallet = close_december(100000, itemized=True)
    original = taxes.closed_returns[2026]
    prior_owed = dict(taxes.outstanding)
    prior_refunds = list(taxes.refunds)
    before = wallet.cash
    with pytest.raises(ValueError, match="state_refund_taxable_fractions"):
        revise(taxes, 2026, allowed_loss(taxes), date(2027, 1, 31))
    assert taxes.closed_returns[2026] is original
    assert taxes.outstanding == prior_owed
    assert taxes.refunds == prior_refunds
    assert wallet.cash == before


def test_confirmed_recovery_enters_federal_income_when_refund_cash_arrives():
    taxes, wallet = close_december(100000, itemized=True, taxable_fraction=1)
    audit = revise(taxes, 2026, allowed_loss(taxes), date(2027, 1, 31))
    assert audit["refund_scheduled"]["taxable"] == 637
    for month in range(1, 5):
        row = advance(taxes, wallet, date(2027, month, 1), date(2027, month + 1, 1))
    assert row["tax_refund_received"] == 2137
    assert taxes.result["federal"]["agi"] == 637
    assert taxes.result["new_jersey"]["gross_income"] == 0
