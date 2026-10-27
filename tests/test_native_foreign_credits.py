"""Native FTC ordering, NIIT separation and cache isolation have independent cash amounts."""

from decimal import Decimal

import pytest

from wealthlab.tax.annual import evaluate, synthetic
from wealthlab.tax.facts import FederalIncome
from wealthlab.tax.filing import Filing
from wealthlab.tax.foreign_credit_facts import ForeignCredits


def ordinary(credits=None, **income):
    case = synthetic().model_copy(
        update=dict(
            filing=Filing(status="single", age_primary=40, age_spouse=0, dependents=[]),
            federal_income=FederalIncome(**(income or dict(wages_primary=Decimal(100000)))),
        )
    )
    return case.model_copy(update=dict(foreign_credits=credits)) if credits else case


def test_native_regular_credit_matches_2025_brackets_and_does_not_change_payroll():
    credits = ForeignCredits(
        regular=Decimal("6724.50"), eligibility="allowed", source="Synthetic permitted FTC"
    )
    result = evaluate(ordinary(credits))["federal"]
    # $84,250 taxable: 1,192.50 + 4,386 + 7,870.50 = $13,449 before credits.
    assert result["regular_tax_before_credits"] == Decimal(13449)
    assert result["foreign_tax_credit"] == Decimal("6724.50")
    assert result["income_tax"] == Decimal("6724.50")
    assert result["employee_payroll"] == Decimal(7650)


def test_regular_credit_does_not_implicitly_pay_amt_or_niit():
    case = ordinary(interest=Decimal(250000))
    regular = evaluate(case)["federal"]["regular_tax_before_credits"]
    credit = ForeignCredits(regular=regular, eligibility="allowed", source="Synthetic cap test")
    result = evaluate(case.model_copy(update=dict(foreign_credits=credit)))["federal"]
    # Form6251: ($250k AMTI - $88,100 exemption) *26% = $42,094, no AMT FTC supplied.
    assert result["amt"] == Decimal(42094)
    assert result["niit"] == Decimal(1900)
    assert result["income_tax"] == Decimal(43994)
    assert evaluate(ordinary())["federal"]["income_tax"] == Decimal(13449)


def test_independently_permitted_amt_credit_uses_its_own_native_input():
    credit = ForeignCredits(
        regular=Decimal(13449),
        alternative_minimum=Decimal(3094),
        eligibility="allowed",
        source="Synthetic fully foreign AMTI; (100000-88100)*26%",
    )
    result = evaluate(ordinary(credit))["federal"]
    assert result["amt"] == 0
    assert result["income_tax"] == 0
    assert result["foreign_tax_credit"] == Decimal(13449)


def test_oversized_regular_credit_is_rejected_instead_of_consuming_amt_tax():
    credit = ForeignCredits(regular=Decimal(100000), eligibility="allowed", source="Invalid cap")
    with pytest.raises(ValueError, match="exceeds regular tax"):
        evaluate(ordinary(credit))


def test_denial_preserves_tax_and_positive_unresolved_credit_is_not_a_default_benefit():
    denied = ForeignCredits(
        regular=Decimal(1000), eligibility="denied", source="Denied synthetic claim"
    )
    assert evaluate(ordinary(denied))["federal"]["income_tax"] == Decimal(13449)
    with pytest.raises(ValueError, match="resolved eligibility"):
        ForeignCredits(regular=Decimal(1000))
