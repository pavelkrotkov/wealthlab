"""Execute one sleeve against the current wallet, after receipts and prior tax arrears.

Later household receipts first repay debt left by a closed margin account.
Net cash movement is applied once; a redemption is not another tax cash event.
The economic account's positive equity and negative-equity liability remain
separate, so borrowing is neither income nor a second reduction in wealth.
"""

from datetime import timedelta

from wealthlab.products.long_short_book import ZERO, equity
from wealthlab.products.long_short_step import advance


def execute(book, sleeve, month, wallet, end):
    before = wallet.cash
    book["outside"] = before
    debt_paid = repay_debt(book)
    row = advance(
        book,
        sleeve.case,
        sleeve.observations[month].model_dump(),
        end - timedelta(days=1),
        month,
        month == len(sleeve.observations) - 1,
    )
    transfer(wallet, book["outside"] - before)
    wallet.balances[sleeve.account_id] = max(ZERO, equity(book))
    row.update(
        recourse_debt_paid=debt_paid,
        account_id=sleeve.account_id,
        long_factor=sleeve.case.long_factor,
        short_factor=sleeve.case.short_factor,
    )
    return row


def transfer(wallet, amount):
    if amount >= 0:
        wallet.deposit(amount)
    elif wallet.pay(-amount) != -amount:
        raise ValueError("Sleeve cannot spend unavailable household collateral cash.")


def repay_debt(book):
    paid = min(book["outside"], book["loan"]) if book["closed"] else ZERO
    book["outside"] -= paid
    book["loan"] -= paid
    return paid
