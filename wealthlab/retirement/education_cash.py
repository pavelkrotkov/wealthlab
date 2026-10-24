"""529 transfers conserve capital; external beneficiaries do not become household cash.

A plan cap is a shared current balance cap, not an annual deposit or gift-tax
allowance. Opening loss basis can exceed market value. Full exit records the
unrecovered loss separately and never fabricates a current tax deduction.
"""

from decimal import Decimal

from wealthlab.household.calendar import money


def contribute(book, item):
    account = book["accounts"][item.destination]
    plan = book["plans"][account.plan]
    limit = max(
        (entry for entry in plan.limits if entry.effective <= item.date),
        key=lambda entry: entry.effective,
    ).maximum_balance
    total = sum(
        book["balances"][a.id]
        for a in book["accounts"].values()
        if a.plan == account.plan and a.beneficiary == account.beneficiary
    )
    allowed = min(item.amount, max(Decimal(0), limit - total))
    paid = min(allowed, book["cash"])
    book["cash"] -= paid
    book["balances"][account.id] += paid
    book["basis"][account.id] += paid
    if plan.njbest:
        book["nj_contributions"] += paid
    book["rows"].append(
        dict(
            id=item.id,
            date=item.date,
            kind="contribution",
            account=account.id,
            requested=item.amount,
            funded=paid,
            blocked_by_limit=item.amount - allowed,
            unfunded=allowed - paid,
        )
    )


def withdraw(book, item):
    account = book["accounts"][item.source]
    balance = book["balances"][account.id]
    paid = min(item.amount, balance)
    returned_basis = release_basis(book, account.id, paid)
    book["balances"][account.id] -= paid
    recipient = account.owner if item.payee == "owner" else account.beneficiary
    internal = item.payee != "institution" and book["people"][recipient].household_cash_member
    if internal:
        book["cash"] += paid
    else:
        book["external"] += paid
    book["rows"].append(
        dict(
            id=item.id,
            date=item.date,
            kind="withdrawal",
            account=account.id,
            recipient=recipient,
            recipient_category="owner" if item.payee == "owner" else "beneficiary",
            payee=item.payee,
            requested=item.amount,
            funded=paid,
            unfilled=item.amount - paid,
            basis_returned=returned_basis,
            earnings=paid - returned_basis,
            to_household_cash=internal,
        )
    )


def release_basis(book, identity, paid):
    """An unfunded request is not an account exit, even after a total market loss.

    Basis survives a zero-value period until an actual funded final withdrawal.
    Later deposits therefore cannot erase the original unrecovered investment.
    """
    balance, basis = book["balances"][identity], book["basis"][identity]
    returned = money(min(balance, basis) * paid / balance) if balance else Decimal(0)
    remaining = basis - returned
    closed = paid > 0 and paid == balance
    book["basis"][identity] = Decimal(0) if closed else remaining
    if closed:
        book["loss_basis"] += remaining
    return returned
