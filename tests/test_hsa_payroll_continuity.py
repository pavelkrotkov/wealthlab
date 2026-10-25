"""Annual eligibility resets preserve shared receipts and count every payroll transfer once."""

from copy import deepcopy
from decimal import Decimal

from wealthlab.household.projection import project
from wealthlab.household.scenario import Scenario
from wealthlab.retirement.hsa_household_example import context
from wealthlab.retirement.hsa_payroll_example import synthetic


def test_second_year_salary_funding_resets_room_but_cannot_reuse_old_receipts():
    original = synthetic()
    data = original.model_dump(mode="json")
    data["end"] = data["incomes"][0]["end"] = "2028-01-01"
    case = deepcopy(data["tax_plan"]["cases"][0])
    case["policy"]["year"] = 2027
    data["tax_plan"]["cases"].append(case)
    work = deepcopy(data["workplace_plan"]["years"][0])
    work["year"] = 2027
    data["workplace_plan"]["years"].append(work)
    plan = data["hsa_plan"]
    plan["years"].append(context(original, 2027))
    groups = [
        data["workplace_plan"]["orders"],
        plan["contributions"],
        plan["withdrawals"],
        plan["payroll"]["orders"],
    ]
    for group in groups:
        group.extend(
            dict(row, id="next_" + row["id"], date=row["date"].replace("2026", "2027"))
            for row in list(group)
        )
    rows = project(Scenario.model_validate(data))
    assert sum(r["hsa_payroll_contributions"] for r in rows) == 12000
    assert sum(r["hsa_withdrawal_cash"] for r in rows) == 3000
    assert rows[-1]["account_balances"]["cash_hsa"] == 14000
    assert rows[-1]["hsa_audit"]["receipt_remaining"]["past_medical"] == 0
    assert [r["annual_tax"]["federal"]["employee_payroll"] for r in (rows[11], rows[23])] == [
        Decimal(8721),
        Decimal(8721),
    ]
