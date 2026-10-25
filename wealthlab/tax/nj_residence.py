"""Conditional person/date/source NJ-1040 and NJ-1040NR return-unit calculations."""

from decimal import Decimal

from wealthlab.tax import nj_residence_deductions as expense
from wealthlab.tax.nj_residence_income import gross, recognized, reconcile, totals
from wealthlab.tax.nj_residence_returns import calculate_unit
from wealthlab.tax.nj_residence_units import units
from wealthlab.tax.nj_residence_validation import validate

ZERO = Decimal(0)


def calculate(filing, income, inputs, year=2025, assume_2025=False, *, profile):
    if year != 2025 and not assume_2025:
        raise ValueError("NJ published move rules are validated for 2025 only.")
    if any(inputs.model_dump().values()):
        raise ValueError(
            "NJ move deductions belong to dated, owner/return-specific period records."
        )
    validate(profile, filing, year)
    reconcile(profile, income)
    groups = units(profile, filing, year)
    expense.validate(profile, groups, year)
    returns = [item for group in groups for item in calculate_unit(profile, group, year)]
    return summary(profile, returns, year)


def summary(profile, returns, year):
    liability = sum((r["income_tax"] for r in returns), ZERO)
    return dict(
        income_tax=liability,
        taxable_income=sum((r["taxable_income"] for r in returns), ZERO),
        total_income=gross(totals(recognized(profile, profile.as_of))),
        gross_income=gross(totals(recognized(profile, profile.as_of))),
        pension_exclusion=ZERO,
        other_exclusion=ZERO,
        business_adjustment=ZERO,
        business_carry=[],
        business_expired=ZERO,
        property_credit=ZERO,
        property_deduction=ZERO,
        below_filing_threshold=all(r["below_filing_threshold"] for r in returns),
        residence_returns=returns,
        residence_inputs=profile.model_dump(mode="json"),
        policy=(
            f"NJ 2025 conditional dated residence/source rules applied to {year}; "
            "foreign/PR tax credits excluded"
        ),
    )
