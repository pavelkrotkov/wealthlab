"""Separate federal section1256 mark resets from independently supplied NJ realization."""

from decimal import Decimal

from wealthlab.products.option_tax import unresolved
from wealthlab.products.option_tax_rows import tax_row


def recognition(state):
    # Prior marks reset federal gain, while NJ continues to the original cash premium.
    result, prior = [], {}
    for row in state.recognition:
        for jurisdiction in ("federal", "nj"):
            if row["physical"]:
                continue
            if jurisdiction == "nj" and row["action"] == "yearend_mark":
                continue
            amount = recognized_amount(row, jurisdiction, prior)
            result.append(option_row(state.case.tax, row, jurisdiction, amount))
    return result


def recognized_amount(row, jurisdiction, prior):
    amount = row["pnl"]
    key = row["leg_id"]
    if jurisdiction == "federal" and row["federal_class"] == "section1256":
        amount -= prior.get(key, Decimal(0))
        prior[key] = row["pnl"]
    return amount


def option_row(tax, row, jurisdiction, amount):
    errors = unresolved(tax, jurisdiction)
    if jurisdiction == "federal" and row["federal_class"] == "unresolved":
        errors.append("leg_classification")
    deferral = getattr(tax, f"{jurisdiction}_deferrals").get(row["id"], Decimal(0))
    fraction = Decimal(row["federal_character"] == "long_term")
    if jurisdiction == "federal" and row["federal_class"] == "section1256":
        fraction = Decimal("0.6")
    return tax_row(row["id"], row["date"], jurisdiction, amount, deferral, fraction, errors)
