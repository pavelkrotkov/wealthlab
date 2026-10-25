"""A cash-only opening share purchase is dated, affordable in native money and uniquely named."""

from decimal import Decimal

from pydantic import TypeAdapter

from wealthlab.household.calendar import money
from wealthlab.household.records import Money


def validate(case):
    purchase = case.opening_stock_purchase
    if purchase is None:
        return
    if purchase.provenance == "unresolved" or purchase.date != case.holdings.as_of:
        raise ValueError("Resolve the opening stock purchase at the exact first accounting date.")
    if case.holdings.lots or case.allow_settlement_loan:
        raise ValueError(
            "Opening stock purchases require no pre-owned lots or settlement borrowing."
        )
    validate_identity(case, purchase)
    cost = money(Decimal(purchase.shares) * case.marks[0].stock) + purchase.fee
    # Reject an unrepresentable lot basis before reserve/account cash can move.
    TypeAdapter(Money).validate_python(cost)


def validate_identity(case, purchase):
    occupied = {leg.id for leg in case.legs} | {f"exercise_{leg.id}" for leg in case.legs}
    if purchase.id in occupied | {"complete_unwind"}:
        raise ValueError("Opening purchase ID collides with an option or generated stock trade.")
