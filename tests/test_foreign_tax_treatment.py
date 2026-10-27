"""Tax eligibility changes conditional US relief without changing actual foreign cash.

Wealth tax and explicit conversion fees remain economic costs. They cannot
become US income-tax credits merely because an assessment is foreign. NJ
liability remains its independent entered return in every treatment.
"""

from decimal import Decimal

import pytest

from wealthlab.household.projection import project
from wealthlab.household.scenario import Scenario
from wealthlab.tax.foreign_tax_example import synthetic


@pytest.mark.parametrize(
    "treatment,credit,blocked",
    [
        ("allowed", "6724.50", False),
        ("denied", "0", False),
        ("unresolved", "0", True),
    ],
)
def test_credit_treatment_preserves_same_foreign_payment_and_separate_state_tax(
    treatment, credit, blocked
):
    data = synthetic().model_dump(mode="json")
    data["foreign_tax_plan"]["schedules"][0]["credit_eligibility"] = treatment
    row = project(Scenario.model_validate(data))[0]
    assert row["foreign_tax_paid"] == Decimal(11000)
    assert row["annual_tax"]["federal"]["foreign_tax_credit"] == Decimal(credit)
    assert bool(row["foreign_tax_unresolved"]) == blocked
    assert row["annual_tax"]["new_jersey"]["income_tax"] > 0


def test_wealth_tax_and_its_fee_use_real_cash_without_becoming_an_income_credit():
    data = synthetic().model_dump(mode="json")
    plan = data["foreign_tax_plan"]
    plan["assessments"][0]["tax_type"] = "wealth"
    plan["schedules"][0].update(
        creditable_fraction="0", income_ids=[], source_income_year=None, fee_per_execution_usd="15"
    )
    row = project(Scenario.model_validate(data))[0]
    assert row["foreign_tax_paid"] == Decimal(11015)
    assert row["annual_tax"]["federal"]["foreign_tax_credit"] == 0
    assert row["foreign_tax_position"] == 0
    assert row["foreign_tax_cash_records"][0]["tax_type"] == "wealth"


def test_denied_us_credit_does_not_silently_classify_a_capital_gain_for_foreign_tax():
    data = synthetic().model_dump(mode="json")
    data["foreign_tax_plan"]["credit_profiles"][0]["eligibility"] = "denied"
    data["tax_plan"]["cases"][0]["federal_income"]["long_term"] = "1000"
    row = project(Scenario.model_validate(data))[0]
    assert row["foreign_tax_paid"] == Decimal(11000)
    assert row["annual_tax"]["federal"]["foreign_tax_credit"] == 0
    assert any("foreign capital" in reason for reason in row["foreign_tax_unresolved"])
    assert row["funding_failure"]
