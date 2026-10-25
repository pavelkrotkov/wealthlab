"""Original salary reductions, personal deposits and employer funding share one HSA."""

from wealthlab.household.scenario import Scenario
from wealthlab.retirement.hsa_household_example import plan as hsa_plan
from wealthlab.retirement.workplace_example import synthetic as workplace


def synthetic():
    scenario = workplace()
    data = scenario.model_dump(mode="json")
    data["name"] = "Synthetic payroll HSA with employee 401k elections"
    data["accounts"].append(
        dict(
            id="cash_hsa",
            owner="person_a",
            currency="USD",
            wrapper="hsa",
            balance="2000",
            monthly_fee="0",
            provenance="illustration",
        )
    )
    plan = hsa_plan(scenario)
    plan.update(
        interest=[],
        contributions=contributions(),
        withdrawals=[
            dict(
                id="reimburse",
                provenance="illustration",
                date="2026-06-15",
                source="cash_hsa",
                amount=2500,
                mode="qualified_only",
                receipt_ids=["past_medical"],
            )
        ],
        payroll=payroll(),
    )
    data["hsa_plan"] = plan
    data["tax_plan"].update(federal_wage_withholding=".20", nj_wage_withholding=".05")
    return Scenario.model_validate(data)


def contributions():
    return [
        dict(
            id=key,
            provenance="illustration",
            date=when,
            destination="cash_hsa",
            source=source,
            amount=amount,
        )
        for key, when, source, amount in (
            ("direct_funding", "2026-01-15", "direct_employer", 500),
            ("personal_deposit", "2026-03-01", "personal_cash", 1000),
        )
    ]


def payroll():
    return dict(
        orders=[
            dict(
                id=f"salary_hsa_{month}",
                provenance="illustration",
                date=f"2026-{month:02}-01",
                owner="person_a",
                destination="cash_hsa",
                amount=500,
            )
            for month in range(1, 13)
        ],
        qualifying_section125_w2_employee_confirmed=True,
        gross_wages_before_salary_reduction_confirmed=True,
        complete_elections_and_no_other_payroll_reductions_confirmed=True,
        nj_salary_reduction_treatment="taxable_wages_assumption",
        timing="monthly_after_employee_401k_before_other_hsa_events",
    )
