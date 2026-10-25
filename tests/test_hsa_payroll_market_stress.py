"""An observed employer crash affects only later work and payroll funding."""

from decimal import Decimal

from wealthlab.markets.household_run import run
from wealthlab.markets.hsa_payroll_example import personal_policy, synthetic
from wealthlab.markets.paths import generate


def test_linked_job_loss_and_rehire_change_capacity_without_erasing_earned_january_pay():
    household, market, binding = synthetic("stress", "early_crash")
    batch = generate(market)
    left = run(household, batch, binding, [0])
    right = run(personal_policy(household), batch, binding, [0])
    rows = left["details"][0]["rows"]
    assert rows[0]["income"] == 10000
    assert rows[1]["income"] == rows[6]["income"] == 0
    assert rows[7]["income"] == 5000
    assert sum(r["hsa_payroll_contributions"] for r in rows) == 3000
    assert right["outcomes"][0]["hsa_personal_deposits"] == 12000
    check_taxes(left["outcomes"][0], right["outcomes"][0])


def check_taxes(left, right):
    assert left["reported_employee_payroll"] == 2448
    assert right["reported_employee_payroll"] == Decimal("2677.50")
    # Different actual funding changes the above-line deduction. A cafeteria
    # FICA advantage alone is not a claim of greater after-tax wealth.
    assert left["ending_nominal_wealth"] - right["ending_nominal_wealth"] == Decimal("-70.50")
