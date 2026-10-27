"""AEAT 2025 common-regime policy rows; special eligibility remains independently supplied."""

import json
from decimal import Decimal
from pathlib import Path

from wealthlab.tax.spain_rates import CATALONIA_WEALTH, WEALTH
from wealthlab.tax.spain_rates import REGIONS as ORIGINAL

POLICY = json.loads(Path(__file__).with_name("spain_regions_2025.json").read_text())
REGIONS = {name: facts["income"] or ORIGINAL[name] for name, facts in POLICY["regions"].items()}


def policy(region):
    facts = POLICY["regions"][region]
    return {
        **facts,
        "year": POLICY["year"],
        "verified": POLICY["verified"],
        "wealth": facts["wealth"] or (CATALONIA_WEALTH if region == "catalonia" else WEALTH),
    }


def bonus(case, ip, sgf):
    """Use the capped solidarity quota before actual-paid IP credit.

    Full minor-quota relief removes only the remaining IP bill. Galicia
    uses independently supplied final relief, including its solidarity offset.
    """
    facts = policy(case.region)
    remaining = max(Decimal(0), ip - case.credits.wealth_foreign - case.credits.wealth_regional)
    if facts["bonus"] == "full":
        return remaining
    if facts["bonus"] == "cantabria" and sgf == 0:
        return remaining
    if facts["bonus"] in ("difference", "cantabria"):
        return max(Decimal(0), ip - sgf)
    return Decimal(0)


def relief_reasons(case):
    """A statutory amount is not evidence that this person qualifies for it."""
    reasons = []
    if case.region == "galicia" and not case.credits.regional_bonus_included_confirmed:
        reasons.append(
            "Galicia requires supplied final regional relief after its solidarity offset."
        )
    if case.wealth_allowance and case.region in REGIONS:
        eligible = policy(case.region)["eligible_minima"]
        if case.wealth_allowance.minimum_eur not in map(Decimal, eligible):
            reasons.append("The supplied wealth minimum needs another regional policy adapter.")
    return reasons
