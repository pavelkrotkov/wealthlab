"""Actual disposed stock has no shareholder settlement or unrecognized basis left.

Internal creditor debt remains visible under the supplied limited-liability
profile; it is never reclassified as a personal liability or erased. An entity
margin liquidation alone cannot certify sale of the investor's stock interest.
"""

from decimal import Decimal, InvalidOperation

from wealthlab.optimization.drilling_state import zero, zeros


def shareholder_closed(state, audit, plan):
    return (
        isinstance(state, dict)
        and state.get("sold") is True
        and zero(state.get("receivable"))
        and "settlement" in state
        and state["settlement"] is None
        and entity_closed(audit.get("ending_entity"), plan)
        and stock_closed(audit.get("tranches"))
    )


def entity_closed(book, plan):
    if not isinstance(book, dict) or book.get("closed") is not True:
        return False
    return zeros(
        {key: book.get(key) for key in ("long", "short", "collateral", "cash", "outside")},
        ("long", "short", "collateral", "cash", "outside"),
    ) and internal_debt(book.get("loan"), plan)


def internal_debt(value, plan):
    return plan.limited_liability_internal_debt_only_assumed_confirmed and nonnegative(value)


def nonnegative(value):
    if isinstance(value, bool):
        return False
    try:
        amount = Decimal(value)
        return amount.is_finite() and amount >= 0
    except (ValueError, TypeError, InvalidOperation):
        return False


def stock_closed(tranches):
    return (
        isinstance(tranches, list) and bool(tranches) and all(tranche_closed(t) for t in tranches)
    )


def tranche_closed(tranche):
    if not isinstance(tranche, dict) or not isinstance(tranche.get("tax"), dict):
        return False
    books = tranche["tax"].get("jurisdictions")
    return (
        isinstance(books, dict)
        and set(books) == {"federal", "new_jersey"}
        and all(tax_closed(book) for book in books.values())
    )


def tax_closed(book):
    return (
        isinstance(book, dict)
        and zeros(
            {key: book.get(key) for key in ("basis", "ordinary_basis")}, ("basis", "ordinary_basis")
        )
        and nonnegative(book.get("elected"))
        and (zero(book.get("elected")) or book.get("included") is True)
    )
