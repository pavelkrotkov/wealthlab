"""Two synthetic tuition years share actual cash with HSA and IRA elections."""

from wealthlab.household.scenario import Scenario
from wealthlab.retirement.hsa_household_example import synthetic as hsa_household


def synthetic():
    data = hsa_household().model_dump(mode="json")
    data["name"] = "Synthetic household 529 tuition, HSA and IRA funding"
    data["accounts"].append(
        dict(
            id="college",
            provenance="illustration",
            owner="person_a",
            wrapper="education",
            currency="USD",
            balance="30000",
            monthly_fee="0",
        )
    )
    data["education_plan"] = plan()
    return Scenario.model_validate(data)


def plan():
    return dict(
        rule_mode="freeze_2026_assumption",
        people=[
            dict(id=identity, provenance="illustration", household_cash_member=internal)
            for identity, internal in (("person_a", True), ("student", False))
        ],
        plans=[
            dict(
                id="njbest",
                provenance="illustration",
                njbest=True,
                limits=[dict(effective="2026-01-01", maximum_balance="525000")],
            )
        ],
        accounts=[
            dict(
                account_id="college",
                beneficiary="student",
                plan="njbest",
                contribution_basis="20000",
            )
        ],
        contributions=[
            dict(
                id=f"save_{year}",
                provenance="illustration",
                date=f"{year}-02-01",
                destination="college",
                amount="6000",
            )
            for year in (2026, 2027)
        ],
        tuition=[
            dict(
                id=f"tuition_{year}",
                provenance="illustration",
                date=f"{year}-09-01",
                source="college",
                amount="12000",
            )
            for year in (2026, 2027)
        ],
        returns=[
            dict(
                id=f"college_growth_{year}",
                provenance="illustration",
                date=f"{year}-06-01",
                account_id="college",
                rate="0.10",
            )
            for year in (2026, 2027)
        ],
        complete_context_confirmed=True,
        qualified_net_expenses_separate_from_other_budgets_confirmed=True,
        contributions_belong_to_filing_unit_confirmed=True,
    )
