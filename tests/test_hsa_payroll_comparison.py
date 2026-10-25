"""Personal and cafeteria deposits share AGI but only qualifying payroll reduces FICA.

The $6,000 employee salary reduction avoids $459 employee FICA at 7.65% in
this below-wage-cap example. No other tax benefit or external wealth appears.
NJ wage inclusion and withholding are identical under the declared profile.
"""

from decimal import Decimal

import pytest

from wealthlab.household.projection import project
from wealthlab.household.scenario import Scenario
from wealthlab.retirement.hsa_payroll_example import synthetic


@pytest.fixture(scope="module")
def pair():
    original = synthetic()
    data = original.model_dump(mode="json")
    plan = data["hsa_plan"]
    salary = plan["payroll"]["orders"]
    plan["payroll"] = None
    plan["contributions"] += [
        dict(**{k: v for k, v in order.items() if k != "owner"}, source="personal_cash")
        for order in salary
    ]
    return project(original), project(Scenario.model_validate(data))


def test_same_agi_and_nj_income_but_only_cafeteria_reduces_employee_payroll(pair):
    salary, personal = (rows[-1] for rows in pair)
    assert (
        salary["annual_tax"]["federal"]["agi"] == personal["annual_tax"]["federal"]["agi"] == 89000
    )
    assert (
        salary["annual_tax"]["federal"]["income_tax"]
        == personal["annual_tax"]["federal"]["income_tax"]
    )
    assert personal["annual_tax"]["federal"]["employee_payroll"] == 9180
    assert salary["annual_tax"]["federal"]["employee_payroll"] == 8721
    assert salary["net_wealth"] - personal["net_wealth"] == Decimal("459")


def test_nj_tax_and_withholding_do_not_disappear_with_federal_exclusion(pair):
    salary, personal = (rows[-1] for rows in pair)
    assert salary["annual_tax"]["new_jersey"] == personal["annual_tax"]["new_jersey"]
    assert salary["annual_tax"]["state_income_tax_deduction_input"] == 4800
    assert personal["annual_tax"]["state_income_tax_deduction_input"] == 4800
    assert pair[0][0]["tax_withheld"] == Decimal("2626.75")
