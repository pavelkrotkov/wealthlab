"""Worksheet H property deduction versus refundable credit, including low-income seniors."""

from decimal import Decimal

from wealthlab.household.calendar import money
from wealthlab.tax.filing import Filing
from wealthlab.tax.nj_facts import NJDeductions
from wealthlab.tax.nj_rates import tax


def property_choice(taxable: Decimal, filing: Filing, inputs: NJDeductions, below: bool) -> dict:
    same_home = filing.status == "separate" and inputs.separate_same_home
    cap, credit = (7500, 25) if same_home else (15000, 50)
    credit = Decimal(credit if inputs.property_eligible else 0)
    if below:
        credit = credit if older_or_disabled(filing, inputs) else Decimal(0)
        return result(Decimal(0), Decimal(0), Decimal(0), credit)
    deduction = (
        min(inputs.qualifying_property_tax, Decimal(cap))
        if inputs.property_eligible
        else Decimal(0)
    )
    before = tax(taxable, filing.status)
    after_base = max(Decimal(0), taxable - deduction)
    after = tax(after_base, filing.status)
    if before - after >= credit:
        return result(after, after_base, deduction, Decimal(0))
    return result(before, taxable, Decimal(0), credit)


def result(tax_due: Decimal, taxable: Decimal, deduction: Decimal, credit: Decimal) -> dict:
    return dict(
        income_tax=money(tax_due - credit),
        taxable_income=taxable,
        property_deduction=deduction,
        property_credit=credit,
    )


def older_or_disabled(filing: Filing, inputs: NJDeductions) -> bool:
    spouse = filing.status == "joint" and filing.age_spouse >= 65
    return filing.age_primary >= 65 or spouse or inputs.blind_disabled_adults > 0
