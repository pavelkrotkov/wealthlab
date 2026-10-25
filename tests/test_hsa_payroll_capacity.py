"""Current-owner gross payroll room is shared by pretax and Roth401k, not old cash."""

from wealthlab.household.projection import project
from wealthlab.household.scenario import Scenario
from wealthlab.retirement.hsa_payroll_example import synthetic


def test_actual_roth_and_pretax_401k_both_consume_current_owner_payroll_room():
    data = synthetic().model_dump(mode="json")
    orders = data["workplace_plan"]["orders"]
    orders[0]["amount"] = "9500"
    roth = dict(orders[-1], date="2026-01-01", amount="500")
    data["workplace_plan"]["orders"] = [orders[0], roth]
    rows = project(Scenario.model_validate(data))
    assert rows[0]["workplace_contributions"] == 10000
    assert rows[0]["hsa_payroll_contributions"] == 0
    assert rows[0]["hsa_payroll_unfilled"] == 500
    assert sum(r["hsa_payroll_contributions"] for r in rows) == 5500
    audit = rows[-1]["hsa_audit"]["orders"][0]
    assert audit["blocked_by_current_wages"] == 500
    assert not any(r["funding_failure"] for r in rows)


def test_spouse_wages_and_large_opening_cash_cannot_fund_primary_salary_reduction():
    data = synthetic().model_dump(mode="json")
    data["incomes"][0]["owner"] = "person_b"
    data["tax_plan"]["income_rules"][0]["federal"] = "wages_spouse"
    rows = project(Scenario.model_validate(data))
    assert sum(r["hsa_payroll_contributions"] for r in rows) == 0
    assert sum(r["hsa_payroll_unfilled"] for r in rows) == 6000
    assert rows[-1]["account_balances"]["cash_hsa"] == 1000
    assert sum(r["hsa_personal_contributions"] for r in rows) == 1000
