"""Synthetic cash HSA reimbursements share receipts across years and fund the household."""

from wealthlab.household.scenario import Scenario
from wealthlab.retirement.hsa_household_inputs import HSAPlan
from wealthlab.retirement.ira_deposit_household_example import synthetic as ira_household


def synthetic():
    data = ira_household().model_dump(mode="json")
    data["name"] = "Synthetic household cash HSA and IRA deposits"
    data["accounts"].append(
        dict(
            id="cash_hsa",
            provenance="illustration",
            owner="person_a",
            currency="USD",
            wrapper="hsa",
            balance="10000",
            monthly_fee="0",
        )
    )
    data["expenses"].append(
        dict(
            id="health_budget",
            provenance="illustration",
            start=data["start"],
            end=data["end"],
            monthly_amount="500",
            currency="USD",
            annual_growth=0,
            category="healthcare",
        )
    )
    case = Scenario.model_validate(data)
    return case.model_copy(update=dict(hsa_plan=HSAPlan.model_validate(plan(case))))


def plan(scenario):
    years = range(scenario.start.year, scenario.end.year)
    return dict(
        years=[context(scenario, year) for year in years],
        medical_receipts=[
            dict(
                id="past_medical",
                provenance="illustration",
                eligible_owners=["person_a"],
                incurred="2025-05-01",
                paid="2025-06-01",
                amount="3000",
                reimbursed_elsewhere="0",
                deducted_federally="0",
                eligibility="qualified_medical",
            )
        ],
        contributions=[
            dict(
                id=f"{kind}_{year}",
                provenance="illustration",
                date=f"{year}-02-01",
                destination="cash_hsa",
                source=kind,
                amount=amount,
            )
            for year in years
            for kind, amount in (("personal_cash", "4000"), ("direct_employer", "1000"))
        ],
        withdrawals=[
            dict(
                id=f"reimburse_{year}_{month}",
                provenance="illustration",
                date=f"{year}-{month}-01",
                source="cash_hsa",
                amount="1000",
                mode="qualified_only",
                receipt_ids=["past_medical"],
            )
            for year in years
            for month in ("03", "09")
        ],
        interest=[
            dict(
                id=f"hsa_interest_{year}",
                provenance="illustration",
                date=f"{year}-06-01",
                account_id="cash_hsa",
                taxable_bank_interest="150",
            )
            for year in years
        ],
        nj_treatment="taxable_bank_interest_assumption",
        conditional_nj_treatment_confirmed=True,
        cash_only_accounts_and_complete_context_confirmed=True,
        receipts_paid_before_projection_confirmed=True,
        employer_funding_excluded_from_other_nj_wages_confirmed=True,
        priority="after_receipts_before_ira_and_current_tax",
    )


def context(scenario, year):
    return dict(
        year=year,
        rule_mode="freeze_2026_assumption",
        married=True,
        owners=[
            dict(
                id=p.id,
                provenance="illustration",
                birth_date=p.birth_date.isoformat(),
                established="2020-01-01" if i == 0 else None,
                months=[
                    dict(
                        month=month,
                        coverage="family",
                        disqualifying_coverage=False,
                        medicare=False,
                        claimable_dependent=False,
                        family_share="1" if i == 0 else "0",
                    )
                    for month in range(1, 13)
                ],
            )
            for i, p in enumerate(scenario.members)
        ],
    )
