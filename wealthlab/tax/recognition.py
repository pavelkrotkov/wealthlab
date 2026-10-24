"""Accumulate recognized amounts once, keeping cash receipts separate from taxable facts."""

from decimal import Decimal

from wealthlab.tax.annual import AnnualCase
from wealthlab.tax.facts import FederalIncome
from wealthlab.tax.nj_facts import NJIncome
from wealthlab.tax.projection_inputs import IncomeRule, TaxEvent


def add_fields(original, additions):
    """Nested models are summed by amount; eligibility flags are never additive."""
    data = original.model_dump()
    for name, value in additions.model_dump().items():
        if isinstance(value, Decimal):
            data[name] += value
    return type(original).model_validate(data)


def scheduled(case: AnnualCase, amounts: dict[str, Decimal], rules: list[IncomeRule]) -> AnnualCase:
    federal, nj = case.federal_income.model_dump(), case.nj_income.model_dump()
    for rule in rules:
        amount = amounts[rule.income_id]
        if rule.federal != "none":
            federal[rule.federal] += amount
        if rule.federal == "qualified_dividends":
            federal["dividends"] += amount
        if rule.new_jersey != "none":
            nj[rule.new_jersey] += amount
    return case.model_copy(
        update={
            "federal_income": FederalIncome.model_validate(federal),
            "nj_income": NJIncome.model_validate(nj),
        }
    )


def event(case: AnnualCase, item: TaxEvent) -> AnnualCase:
    fed = add_fields(case.federal_income, item.federal)
    nj = add_fields(case.nj_income, item.new_jersey)
    business = add_fields(nj.business, item.new_jersey.business)
    retirement = add_fields(nj.retirement, item.new_jersey.retirement)
    # These eligibility settings are annual facts, not dated amounts. Events can
    # add owner-qualified income, but cannot silently grant special eligibility.
    nj = nj.model_copy(update={"business": business, "retirement": retirement})
    deductions = case.nj_deductions.model_copy(
        update={"njbest": case.nj_deductions.njbest + item.njbest_contributions}
    )
    return case.model_copy(
        update={"federal_income": fed, "nj_income": nj, "nj_deductions": deductions}
    )


def social_cash(amounts, rules):
    return sum((amounts[r.income_id] for r in rules if r.federal == "social_security"), Decimal(0))
