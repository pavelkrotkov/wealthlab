"""A $10k original-year gain revision changes positions, not actual earlier cash.

The closed high-income case stays in the 15% federal long-gain band and the
6.37% NJ bracket. Its revised liability falls by $1,500 plus $637. Paid tax
becomes a delayed receivable; unpaid tax instead reduces the outstanding bill.
"""

from datetime import date

from tests.return_reconciliation_cases import allowed_loss, close_december
from tests.test_closed_return_positions import advance
from wealthlab.tax.return_reconciliation import revise


def test_paid_tax_becomes_a_delayed_refund_without_cash_on_the_revision_date():
    taxes, wallet = close_december(100000)
    before = wallet.cash
    audit = revise(taxes, 2026, allowed_loss(taxes), date(2027, 1, 31))
    assert wallet.cash == before
    assert sum(audit["new_receivable"].values()) == 2137
    assert taxes.owed == 0
    for month in range(1, 5):
        row = advance(taxes, wallet, date(2027, month, 1), date(2027, month + 1, 1))
    assert row["tax_refund_received"] == 2137
    assert wallet.cash == before + 2137
    assert sum(taxes.closed_returns[2026].positions()[1].values()) == 0


def test_unpaid_tax_is_reduced_instead_of_becoming_a_second_refund():
    taxes, wallet = close_december(0)
    original = taxes.owed
    audit = revise(taxes, 2026, allowed_loss(taxes), date(2027, 1, 31))
    assert taxes.owed == original - 2137
    assert sum(audit["new_receivable"].values()) == 0
    assert wallet.cash == 0


def test_an_early_refund_assumption_cannot_pay_a_new_revision_before_it_is_known():
    taxes, wallet = close_december(100000, refund_month=1)
    before = wallet.cash
    audit = revise(taxes, 2026, allowed_loss(taxes), date(2027, 1, 31))
    assert audit["refund_scheduled"]["date"] == date(2027, 2, 1)
    january = advance(taxes, wallet, date(2027, 1, 1), date(2027, 2, 1))
    assert january["tax_refund_received"] == 0
    assert wallet.cash == before
    february = advance(taxes, wallet, date(2027, 2, 1), date(2027, 3, 1))
    assert february["tax_refund_received"] == 2137


def test_already_received_refund_is_not_paid_twice_after_the_revision():
    taxes, wallet = close_december(0, refund_month=1, overpaid=True)
    first = advance(taxes, wallet, date(2027, 1, 1), date(2027, 2, 1))
    assert first["tax_refund_received"] == 1500
    audit = revise(taxes, 2026, allowed_loss(taxes), date(2027, 1, 31))
    assert sum(audit["new_receivable"].values()) == 2137
    assert wallet.cash == 1500
    second = advance(taxes, wallet, date(2027, 2, 1), date(2027, 3, 1))
    assert second["tax_refund_received"] == 2137
    assert wallet.cash == 3637
