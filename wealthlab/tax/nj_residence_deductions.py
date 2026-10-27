"""Reuse NJ deductions with actual period expenses and prorated basic exemptions."""

from decimal import Decimal

from wealthlab.household.calendar import money
from wealthlab.tax.nj_deductions import deductions, exemptions
from wealthlab.tax.nj_facts import NJDeductions

# Special eligibility, shared annual caps and property/education credits need
# their own supplied allocation, rather than an invented fraction of a total.
SUPPORTED = {"medical", "qualified_msa", "self_employed_health", "alimony", "conservation"}


def period_inputs(profile, unit, period, days):
    records = matching_records(profile, unit, period)
    values = {name: Decimal(0) for name in SUPPORTED}
    for row in records:
        if row.paid_on > profile.as_of:
            continue
        if row.paid_on not in days or not row.eligibility_and_period_allocation_assumed_confirmed:
            raise ValueError(
                "NJ deduction expenses require confirmed actual payment in this period."
            )
        for name in SUPPORTED:
            values[name] += getattr(row.inputs, name)
    return NJDeductions.model_validate(values)


def validate(profile, return_units, year):
    owner_groups = {frozenset(u["owners"]) for u in return_units}
    for row in profile.deductions:
        if len(row.owners) != len(set(row.owners)) or frozenset(row.owners) not in owner_groups:
            raise ValueError("NJ period deduction owners must match one actual return unit.")
        if row.paid_on.year != year:
            raise ValueError("NJ deduction payment must belong to its annual calendar year.")
        if unsupported_inputs(row):
            raise ValueError("Special NJ move deduction/exemption allocation is not supported.")


def amount(gross, filing, inputs, count):
    basic = exemptions(filing, NJDeductions())
    actual = deductions(gross, filing, inputs) - basic
    return actual + prorated_exemption(filing, count)


def matching_records(profile, unit, period):
    return [
        r for r in profile.deductions if set(r.owners) == set(unit["owners"]) and r.period == period
    ]


def unsupported_inputs(row):
    return any(value for name, value in row.inputs.model_dump().items() if name not in SUPPORTED)


def prorated_exemption(filing, count):
    return money(exemptions(filing, NJDeductions()) * Decimal(count) / 12)
