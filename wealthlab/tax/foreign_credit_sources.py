"""Dated source facts reconcile to the same annual federal filing unit.

All-source gross amounts determine standard-deduction apportionment. Income
kind and credit basket remain independently supplied classifications; US
source rows still belong in the worldwide denominator. Historical source
rows remain available for an original-year payment or refund identity.
"""

from decimal import Decimal

from wealthlab.tax.facts import FederalIncome

ZERO = Decimal(0)
KINDS = {
    "interest": "interest",
    "dividends": "dividends",
    "ordinary": "ordinary_noninvestment_income",
    "long_term": "long_term",
}
SUPPORTED = {"wages_primary", "wages_spouse", *KINDS.values()} - {"long_term"}
BASKETS = {
    "wages": "general",
    "ordinary": "general",
    "interest": "passive",
    "dividends": "passive",
    "long_term": "passive",
}


def income_facts(case):
    values = {field: ZERO for field in FederalIncome.model_fields}
    for row in case.income:
        if row.value.date.year != case.annual.policy.year:
            continue
        field = f"wages_{case.people[row.owner_id]}" if row.kind == "wages" else KINDS[row.kind]
        values[field] += row.value.dollars()
    return values


def reconcile(case):
    from wealthlab.tax.pr_execution_credit_sources import extra_source_fields

    expected = income_facts(case)
    fields = SUPPORTED | extra_source_fields(case)
    actual = case.annual.federal_income.model_dump()
    if any(expected[field] != actual[field] for field in fields):
        raise ValueError(
            "Dated source rows must exactly reconcile to annual recognized federal income."
        )
    validate_income_baskets(case)
    if case.annual.pr_federal is not None:
        from wealthlab.tax.pr_execution_credit_sources import included

        included(case)


def validate_income_baskets(case):
    for row in case.income:
        if row.basket != BASKETS[row.kind]:
            raise ValueError(
                "Use the independently confirmed ordinary income basket for each kind."
            )
