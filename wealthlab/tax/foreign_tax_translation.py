"""Separate actual bank cash from the levy currency used for paid-tax translation.

The explicit levy value keeps its own paid-date spot quote. Cash conversion
and tax translation must reconcile before this bounded profile executes; bank
fees stay in the separate existing fee field. This does not classify a general
currency-account gain/loss or infer a deductible conversion cost.
"""


def tax_value(record):
    return record.tax_value or record.value


def validate(record):
    tax = tax_value(record)
    if tax.date != record.value.date:
        raise ValueError("Paid-tax translation date must match the actual payment/receipt date.")
    if tax.currency == "USD" and tax.usd_per_unit != 1:
        raise ValueError("USD tax recognition requires unit conversion.")
    if tax.dollars() != record.value.dollars():
        raise ValueError(
            "Actual cash and levy-currency spot translation must reconcile; "
            "supply conversion costs separately rather than inferring tax treatment."
        )
