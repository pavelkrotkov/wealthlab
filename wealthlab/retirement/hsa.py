"""Dated cash HSA allocation; federal tax ingredients remain separate from cash funding."""

from datetime import date
from decimal import Decimal

from wealthlab.household.calendar import money
from wealthlab.retirement import hsa_receipts
from wealthlab.retirement.contribution_assumptions import rule_year
from wealthlab.retirement.contribution_inputs import CashReceipt
from wealthlab.retirement.hsa_capacity import budgets
from wealthlab.retirement.hsa_inputs import HSACase, HSAContribution, HSAInterest


def run(case: HSACase):
    """Cash and HSA balances conserve principal independently of the tax report.

    Direct employer funding and bank interest are external additions. Personal
    funding and reimbursements move existing capital; tax deductions are not
    deposited as cash. Only funded requests consume owner contribution room.
    """
    book: dict = opening(case)
    for _, _, _, item in timeline(case):
        apply(book, item)
    nj = None
    if case.nj_treatment != "unconfirmed":
        nj = dict(
            employer_contributions=book["employer"],
            taxable_interest=book["interest"],
            personal_deduction=Decimal(0),
            mode=case.nj_treatment,
        )
    return dict(
        year=case.year,
        rule_base_year=rule_year(case),
        rule_mode=case.rule_mode,
        cash=book["cash"],
        account_balances=book["balances"],
        contribution_limits=book["limits"],
        contributions_funded=book["used"],
        receipt_remaining=book["receipt_remaining"],
        orders=book["rows"],
        personal_federal_deduction=book["personal"],
        external_employer_funding=book["employer"],
        cash_interest=book["interest"],
        new_jersey=nj,
        sources=[
            "https://www.irs.gov/publications/p969",
            "https://www.irs.gov/pub/irs-drop/rp-25-19.pdf",
        ],
    )


def timeline(case):
    # Receipts and bank interest, contributions, then withdrawals on the same day.
    groups = [case.cash_receipts, case.interest, case.contributions, case.withdrawals]
    events = [
        (item.date, priority, index, item)
        for priority, group in enumerate(groups)
        for index, item in enumerate(group)
    ]
    return sorted(events, key=lambda event: event[:3])


def apply(book, item):
    if isinstance(item, CashReceipt):
        book["cash"] += item.amount
    elif isinstance(item, HSAInterest):
        book["balances"][item.account_id] += item.taxable_bank_interest
        book["interest"] += item.taxable_bank_interest
    elif isinstance(item, HSAContribution):
        contribute(book, item)
    else:
        withdraw(book, item)


def contribute(book, item):
    owner = book["accounts"][item.destination].owner
    allowed = min(item.amount, max(Decimal(0), book["limits"][owner] - book["used"][owner]))
    paid = min(allowed, book["cash"]) if item.source == "personal_cash" else allowed
    if item.source == "personal_cash":
        book["cash"] -= paid
        book["personal"] += paid
    else:
        book["employer"] += paid
    book["balances"][item.destination] += paid
    book["used"][owner] += paid
    book["rows"].append(
        dict(
            id=item.id,
            date=item.date,
            kind=item.source,
            owner=owner,
            account=item.destination,
            requested=item.amount,
            funded=paid,
            blocked_by_limit=item.amount - allowed,
            unfunded=allowed - paid,
        )
    )


def withdraw(book, item):
    owner = book["owners"][book["accounts"][item.source].owner]
    allowed = item.amount
    if item.mode == "qualified_only":
        allowed = min(allowed, hsa_receipts.capacity(book, item, owner))
    investments = book.get("investments")
    if investments is not None:
        investments.fund(book, item.source, allowed, item.date)
    paid = min(allowed, book["balances"][item.source])
    qualified = hsa_receipts.consume(book, item, owner, paid)
    taxable = paid - qualified
    penalty = additional_tax(owner, item.date, taxable)
    book["balances"][item.source] -= paid
    book["cash"] += paid
    if investments is not None:
        investments.sync_cash(book)
    book["rows"].append(
        dict(
            id=item.id,
            date=item.date,
            kind="withdrawal",
            owner=owner.id,
            account=item.source,
            mode=item.mode,
            requested=item.amount,
            funded=paid,
            unfilled=item.amount - paid,
            qualified=qualified,
            federal_taxable=taxable,
            federal_additional_tax=penalty,
        )
    )


def additional_tax(owner, when, taxable):
    # This layer excludes death/beneficiary transfers; disability is a supplied date.
    sixtyfive = date(
        owner.birth_date.year + 65,
        owner.birth_date.month,
        min(owner.birth_date.day, 28) if owner.birth_date.month == 2 else owner.birth_date.day,
    )
    disabled = owner.disabled_since is not None and when >= owner.disabled_since
    return Decimal(0) if when >= sixtyfive or disabled else money(taxable * Decimal(".20"))


def opening(case):
    return dict(
        owners={p.id: p for p in case.owners},
        accounts={a.id: a for a in case.accounts},
        balances={a.id: a.balance for a in case.accounts},
        cash=case.opening_cash,
        receipts={r.id: r for r in case.medical_receipts},
        receipt_remaining={
            r.id: r.amount - r.reimbursed_elsewhere - r.deducted_federally
            for r in case.medical_receipts
        },
        limits=budgets(case),
        used={p.id: Decimal(0) for p in case.owners},
        personal=Decimal(0),
        employer=Decimal(0),
        interest=Decimal(0),
        rows=[],
    )
