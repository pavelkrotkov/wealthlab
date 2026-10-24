"""Fund dated 529 requests without turning projected deductions into available cash."""

from decimal import Decimal

from wealthlab.household.calendar import money
from wealthlab.retirement.contribution_inputs import CashReceipt
from wealthlab.retirement.distribution_inputs import AccountReturn
from wealthlab.retirement.education_cash import contribute, withdraw
from wealthlab.retirement.education_inputs import EducationContribution
from wealthlab.retirement.education_tax import reconcile


def run(case):
    book = opening(case)
    for _, _, _, item in timeline(case):
        apply(book, item)
    tax = reconcile(case, book)
    return dict(
        year=case.year,
        cash=book["cash"],
        account_balances=book["balances"],
        contribution_basis=book["basis"],
        orders=book["rows"],
        external_disbursements=book["external"],
        investment_return=book["return"],
        closed_account_loss_basis=book["loss_basis"],
        **tax,
    )


def opening(case):
    return dict(
        case=case,
        cash=case.opening_cash,
        balances={a.id: a.balance for a in case.accounts},
        basis={a.id: a.contribution_basis for a in case.accounts},
        accounts={a.id: a for a in case.accounts},
        plans={p.id: p for p in case.plans},
        people={p.id: p for p in case.people},
        rows=[],
        external=Decimal(0),
        nj_contributions=Decimal(0),
        **{"return": Decimal(0)},
        loss_basis=Decimal(0),
    )


def timeline(case):
    # Receipt, net return, contribution, then withdrawal; list order breaks ties.
    groups = [case.receipts, case.returns, case.contributions, case.withdrawals]
    events = [
        (item.date, priority, index, item)
        for priority, group in enumerate(groups)
        for index, item in enumerate(group)
    ]
    return sorted(events, key=lambda event: event[:3])


def apply(book, item):
    if isinstance(item, CashReceipt):
        book["cash"] += item.amount
    elif isinstance(item, AccountReturn):
        change = money(book["balances"][item.account_id] * item.rate)
        book["balances"][item.account_id] += change
        book["return"] += change
    elif isinstance(item, EducationContribution):
        contribute(book, item)
    else:
        withdraw(book, item)
