"""Supplied zero-cash recognition enters the ordinary tax ledger exactly once.

A tax allocation is neither economic alpha nor a second receipt. Its permitted
characters are the existing explicit capital/passive/interest/dividend model;
generic ordinary income or plan eligibility is not inferred from a trade.
"""

from wealthlab.products.conditional_allocations import events
from wealthlab.tax.projection_validation import validate_event

FEDERAL = {
    "interest",
    "tax_exempt_interest",
    "dividends",
    "qualified_dividends",
    "short_term",
    "long_term",
    "allowed_passive_income",
}


def validate(sleeve, scenario):
    for item in sleeve.allocations:
        if not scenario.start <= item.date < scenario.end:
            raise ValueError(
                "Supplied sleeve allocations must fall inside the household projection."
            )
        if any(value for key, value in item.federal.model_dump().items() if key not in FEDERAL):
            raise ValueError("Unsupported federal character in supplied sleeve allocation.")
        validate_nj(item.new_jersey)
        for recognized in events(item):
            validate_event(recognized)


def validate_nj(income):
    if income.wages or income.pension or income.business.carry:
        raise ValueError(
            "Sleeve allocations cannot introduce wages, pensions or manual business carry."
        )
    if any(income.retirement.model_dump().values()):
        raise ValueError("Sleeve allocations cannot introduce retirement exemptions.")
