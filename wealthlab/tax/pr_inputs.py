"""Reconcile worldwide source rows to the independent mainland annual baseline."""

from calendar import isleap
from decimal import Decimal

from wealthlab.tax.facts import FederalIncome

FIELDS = {
    "interest": "interest",
    "dividends": "dividends",
    "ordinary": "ordinary_noninvestment_income",
    "long_term": "long_term",
}


def income(rows):
    values = {name: Decimal(0) for name in FederalIncome.model_fields}
    for row in rows:
        field = f"wages_{row.owner}" if row.kind == "wages" else FIELDS[row.kind]
        values[field] += row.federal_amount
        values["qualified_dividends"] += row.qualified_dividends
    return FederalIncome(**values)


def validate(case):
    year = case.baseline.policy.year
    if any(row.received.year != year for row in case.income):
        raise ValueError("Every income receipt must fall in the comparison tax year.")
    validate_presence(case, year)
    if income(case.income) != case.baseline.federal_income:
        raise ValueError("Source rows must exactly reconcile to baseline federal income.")
    if case.baseline.filing.status != "joint" and any(row.owner == "spouse" for row in case.income):
        raise ValueError("Spouse rows require joint filing.")


def validate_presence(case, year):
    if any(
        getattr(case, owner).presence_days > 365 + isleap(year)
        for owner in {row.owner for row in case.income}
    ):
        raise ValueError("Presence days exceed the actual tax-year length.")
