"""Creditability and basket knowledge remain independent of an observed cash payment.

A payment can be economically real while its credit is denied or unresolved.
Taxes on excluded income need an explicit supported allocation. An unresolved
basket or credit source blocks that tax scope, preserving actual cash in the
output instead of treating missing eligibility as a benefit.
"""

from wealthlab.tax.pr_execution_credit_sources import excluded_tax_reasons


def classification_reasons(case):
    result = []
    rows = [*case.income, *case.tax_cash, *case.opening_carries]
    if any(r.basket not in {"general", "passive"} for r in rows):
        result.append(
            "Resolve baskets; treaty-resourced and other profiles require another adapter."
        )
    result.extend(tax_reasons(case))
    result.extend(passive_reasons(case))
    return result + excluded_tax_reasons(case)


def tax_reasons(case):
    result = []
    if any(r.eligibility == "unresolved" for r in case.tax_cash):
        result.append("Tax creditability is unresolved; observed cash remains visible.")
    if any(r.creditable_native and not r.included_income_confirmed for r in case.tax_cash):
        result.append("Confirm that creditable taxes relate only to US-included income.")
    return result + domestic_tax_reasons(case.tax_cash)


def domestic_tax_reasons(rows):
    if any(r.country == "US" and r.creditable_native for r in rows):
        return ["US tax payments are not foreign-tax-credit inputs."]
    return []


def passive_reasons(case):
    passive = any(
        r.basket == "passive" for r in [*case.income, *case.tax_cash, *case.opening_carries]
    )
    if passive and not case.passive_category_no_special_reclassification_confirmed:
        return ["Passive high-tax/special reclassification requires independent confirmation."]
    return []
