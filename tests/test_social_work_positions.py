"""Government adjustments conserve wealth and cannot fund earlier cash or another recipient."""

from datetime import date
from decimal import Decimal as D

from wealthlab.retirement.social_work_positions import Positions


def entry(member, amount, due):
    return dict(
        member=member,
        amount=D(amount),
        due_date=due,
        known_date=date(2027, 1, 1),
        payment_month=date(2026, 6, 1),
    )


def test_receivable_offsets_own_due_debt_before_cash_and_never_another_owner():
    when = date(2027, 5, 1)
    book = Positions(
        [
            entry("a", "491", when),
            entry("a", "600", date(2027, 6, 1)),
            entry("a", "-800", when),
            entry("b", "-1000", when),
        ]
    )
    book.observe(date(2026, 12, 1), True)
    assert book.snapshot("a")["government_receivable"] == 0
    book.observe(when, True)
    paid = book.settle("a", when, D(562), D("0.50"))
    assert paid == dict(
        refund_cash=D(0), refund_debt_offset=D(491), recovered_overpayment=D(281), net_cash=D(281)
    )
    assert book.snapshot("a") == dict(
        government_receivable=D(600), government_overpayment_debt=D(28)
    )
    assert book.snapshot("b")["government_overpayment_debt"] == 1000
    book.observe(when, True)
    paid = book.settle("a", date(2027, 6, 1), D(562), D("0.50"))
    assert paid["refund_cash"] == 572
    assert paid["net_cash"] == 1134
