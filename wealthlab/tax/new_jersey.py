"""2025 full-year NJ resident income-tax core, with separate category/basis inputs."""

from decimal import Decimal

from wealthlab.tax.filing import Filing
from wealthlab.tax.nj_business import adjustment
from wealthlab.tax.nj_deductions import deductions
from wealthlab.tax.nj_facts import NJDeductions, NJIncome
from wealthlab.tax.nj_property import property_choice
from wealthlab.tax.nj_retirement import exclusions


def calculate(
    filing: Filing,
    income: NJIncome,
    inputs: NJDeductions,
    year: int = 2025,
    assume_2025: bool = False,
) -> dict:
    """Published 2025 rules only; future-regime scaling belongs to the annual adapter."""
    if year != 2025 and not assume_2025:
        raise ValueError("NJ published rules are validated for 2025 only.")
    business = adjustment(income.business, year)
    ordinary = income.wages + income.interest + income.dividends + income.other
    total = (
        ordinary
        + max(Decimal(0), income.dispositions)
        + income.pension
        + business["regular_income"]
    )
    earned = income.wages + sum(
        max(Decimal(0), value)
        for value in (
            income.business.business,
            income.business.partnership,
            income.business.s_corporation,
        )
    )
    excluded = exclusions(total, income.pension, earned, income.retirement, filing.status)
    gross = max(Decimal(0), total - sum(excluded.values()))
    taxable = max(Decimal(0), gross - deductions(gross, filing, inputs) - business["adjustment"])
    below = gross <= (10000 if filing.status in {"single", "separate"} else 20000)
    result = property_choice(taxable, filing, inputs, below)
    return dict(
        result,
        total_income=total,
        gross_income=gross,
        **excluded,
        business_adjustment=business["adjustment"],
        business_carry=business["carry"],
        business_expired=business["expired"],
        below_filing_threshold=below,
        policy=(
            f"NJ 2025 full-year rules applied to {year}; "
            "special credits and other-state credits excluded"
        ),
    )
