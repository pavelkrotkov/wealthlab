"""Explicit far-future assumptions, independent of an actual household or future statute."""

from wealthlab.retirement.contribution_example import data
from wealthlab.retirement.contribution_inputs import ContributionCase
from wealthlab.retirement.hsa_example import synthetic as hsa_example
from wealthlab.retirement.hsa_inputs import HSACase


def retirement(year=2050, birth="1990-06-15"):
    payload = data()
    payload.update(year=year, rule_mode="freeze_2026_assumption", opening_cash="1000000")
    payload["contributors"][0].update(birth_date=birth, traditional_ira_magi="0", roth_ira_magi="0")
    for order in payload["orders"]:
        order["date"] = f"{year}-01-15"
    return ContributionCase.model_validate(payload)


def hsa(year=2050, birth="1995-08-31"):
    payload = hsa_example().model_dump(mode="json")
    payload.update(
        year=year, rule_mode="freeze_2026_assumption", opening_cash="20000", married=False
    )
    payload["owners"] = payload["owners"][:1]
    payload["owners"][0]["birth_date"] = birth
    for month in payload["owners"][0]["months"]:
        month.update(coverage="self", medicare=False)
    payload["accounts"] = payload["accounts"][:1]
    payload["contributions"] = [
        dict(
            id="future_contribution",
            provenance="assumption",
            date=f"{year}-01-15",
            destination="hsa",
            source="personal_cash",
            amount="20000",
        )
    ]
    payload.update(interest=[], withdrawals=[], medical_receipts=[])
    return HSACase.model_validate(payload)
