"""Generated claim cash is a transfer into household cash, never an extra asset pool."""

from decimal import Decimal

from wealthlab.household.projection import project
from wealthlab.household.storage import loads
from wealthlab.retirement.social_household import prepare
from wealthlab.retirement.social_household_example import synthetic


def test_cash_and_tax_reconcile_without_payroll_or_nj_benefit_income():
    case = synthetic()
    rows = project(case)
    assert sum(r["social_security_cash"] for r in rows) == 152250
    assert rows[-1]["closing_cash"] == 144250
    assert rows[-1]["net_wealth"] == 244250


def test_social_security_taxable_portion_matches_the_joint_worksheet():
    rows = project(synthetic())
    # Joint income12000 plus half of52200 benefits =38100; half of the6100
    # excess over32000 is taxable. NJ excludes the full Social Security amount.
    annual = rows[-1]["annual_tax"]
    assert annual["federal"]["gross_social_security"] == 52200
    assert annual["federal"]["taxable_social_security"] == 3050
    assert annual["federal"]["agi"] == 15050
    assert annual["federal"]["employee_payroll"] == 0
    assert annual["new_jersey"]["income_tax"] == 0


def test_serialization_and_materialization_preserve_a_single_source():
    case = synthetic()
    restored = loads(case.model_dump_json())
    assert restored == case
    prepared = prepare(case)
    assert prepared.social_security is None
    assert prepare(prepared) == prepared
    assert case.social_security is not None
    assert len(case.incomes) == 1
    assert sum(i.monthly_amount for i in prepared.incomes[1:]) == Decimal(152250)
