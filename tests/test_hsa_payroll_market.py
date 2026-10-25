"""Same requested deposits diverge after retirement; FICA remains separately measurable.

Reduced hours followed by retirement produce $90,000 gross wages. The $6,000
salary policy reduces employee FICA from $6,885 to $6,426. Personal deposits
can continue from savings after retirement, funding $12,000. Their extra
$6,000 changes asset location but creates no current refund without taxable
income; it is not another $6,000 of household wealth or a pure tax benefit.
"""

from decimal import Decimal

import pytest

from wealthlab.markets.household_run import paired, run
from wealthlab.markets.hsa_payroll_example import personal_policy, synthetic
from wealthlab.markets.paths import generate


@pytest.fixture(scope="module")
def comparison():
    household, market, binding = synthetic()
    batch = generate(market)
    original = household.model_dump_json()
    left = run(household, batch, binding, [0])
    right = run(personal_policy(household), batch, binding, [0])
    assert household.model_dump_json() == original
    return left, right


def test_actual_contributions_differ_when_personal_deposits_continue_after_retirement(comparison):
    left, right = (r["outcomes"][0] for r in comparison)
    assert left["hsa_salary_reductions"] == 6000
    assert left["hsa_salary_elections_unfilled"] == 6000
    assert right["hsa_personal_deposits"] == 12000
    assert left["hsa_ending_gross_assets"] == 8000
    assert right["hsa_ending_gross_assets"] == 14000


def test_fica_difference_is_not_an_external_income_or_a_second_personal_deduction(comparison):
    left, right = (r["outcomes"][0] for r in comparison)
    assert left["reported_employee_payroll"] == 6426
    assert right["reported_employee_payroll"] == 6885
    assert left["ending_nominal_wealth"] - right["ending_nominal_wealth"] == 459
    assert right["reported_tax_liability"] - left["reported_tax_liability"] == 459
    assert left["provisional_tax_years"] == left["partial_tax_years"] == []
    assert paired(*comparison)[0]["reported_tax_liability_change"] == 459


def test_matched_batches_keep_actual_cash_tax_changes_separate_from_assessments(comparison):
    left, right = comparison
    differences = paired(left, right)[0]
    assert left["batch_id"] == right["batch_id"]
    assert differences["net_cash_taxes_paid_change"] == (
        right["outcomes"][0]["net_cash_taxes_paid"] - left["outcomes"][0]["net_cash_taxes_paid"]
    )
    assert left["outcomes"][0]["reported_employee_payroll"] == Decimal("6426")
