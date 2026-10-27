"""An actual later wage receipt pays an earlier US bill after its PR assessment date."""

from calendar import monthrange
from copy import deepcopy

from wealthlab.household.scenario import Scenario
from wealthlab.tax.annual import Payments
from wealthlab.tax.jurisdiction_execution_example import native_pr


def late_payment():
    data = native_pr().model_dump(mode="json")
    data["accounts"][0]["balance"] = "0"
    data["end"] = "2027-01-01"
    plan, foreign = data["tax_plan"], data["foreign_tax_plan"]
    future = future_case(plan["cases"][0])
    plan["cases"].append(future)
    plan["events"] = [
        dict(
            date="2026-01-31",
            description="Actual next-year employer wage receipt",
            cash_received="60000",
            federal=dict(wages_primary="60000"),
            new_jersey=dict(wages="60000"),
        )
    ]
    profile = deepcopy(foreign["credit_profiles"][0])
    profile.update(annual=future, as_of="2026-12-31")
    for row in profile["income"]:
        row["value"].update(date="2026-01-31", amount="30000")
    foreign["credit_profiles"].append(profile)
    foreign["quotes"].extend(
        dict(
            date=f"2026-{month:02d}-{monthrange(2026, month)[1]}",
            currency="USD",
            usd_per_unit="1",
            source="Synthetic actual dated unit USD quote",
        )
        for month in range(1, 13)
    )
    return Scenario.model_validate(data)


def future_case(original):
    case = deepcopy(original)
    case["policy"].update(year=2026, mode="freeze_2025")
    case.update(
        nj_regime="freeze_2025", pr_federal=None, payments=Payments().model_dump(mode="json")
    )
    case["federal_income"]["wages_primary"] = "0"
    case["nj_income"]["wages"] = "0"
    case["filing"]["age_primary"] = 41
    return case
