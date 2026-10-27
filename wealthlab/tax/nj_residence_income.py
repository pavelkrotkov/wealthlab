"""State source rows reconcile worldwide NJ amounts before residence filtering.

Foreign wages are not removed from the raw NJ denominator merely because the
person moved. Actual nonresident source treatment is supplied independently;
personal pension/annuity/IRA income classified on line 22 has no columnB entry.
"""

from decimal import Decimal

from wealthlab.tax.nj_facts import NJIncome

ZERO = Decimal(0)
FIELDS = {"wages", "interest", "dividends", "dispositions", "pension", "other"}


def totals(rows):
    values = {field: ZERO for field in FIELDS}
    for row in rows:
        values[row.kind] += row.amount
    return values


def gross(values):
    return sum((v if k != "dispositions" else max(ZERO, v) for k, v in values.items()), ZERO)


def recognized(profile, when):
    return [row for row in profile.income if row.received <= when]


def reconcile(profile, income):
    expected = totals(recognized(profile, profile.as_of))
    if any(expected[field] != getattr(income, field) for field in FIELDS):
        raise ValueError(
            "Dated NJ source rows must reconcile exactly to worldwide NJ recognized income."
        )
    unsupported = income.business.model_dump()
    if any(unsupported.values()):
        raise ValueError(
            "NJ move business categories/carries require a separately supported profile."
        )
    if any(income.retirement.model_dump().values()):
        raise ValueError("Owner-qualified NJ move retirement exclusions require another profile.")
    if income.pension and profile.retirement_exclusions != "denied":
        raise ValueError("This move profile requires explicitly denied retirement exclusions.")


def columns(rows, resident_days):
    resident = [r for r in rows if r.received in resident_days]
    outside = [r for r in rows if r.received not in resident_days]
    sourced = sourced_rows(outside)
    return totals(resident), totals(outside), totals(sourced)


def sourced_rows(outside):
    if any(unresolved_source(r) for r in outside):
        raise ValueError("Nonresident NJ sourcing is unresolved; no favorable zero is assumed.")
    return [r for r in outside if sourced_nonpension(r)]


def to_income(profile):
    return NJIncome.model_validate(totals(profile.income))


def unresolved_source(row):
    return row.nj_source == "unresolved" and row.kind != "pension"


def sourced_nonpension(row):
    return row.nj_source == "allowed" and row.kind != "pension"
