"""Actual two-call corporation cases with independent input returns and financing rates."""

from qoz_cases import flat

from wealthlab.household.scenario import Scenario


def distressed(second_call=True, confirmed=True):
    data = flat().model_dump(mode="json")
    plan = data["qoz_plan"]
    plan.update(federal="denied", new_jersey="denied")
    data["lot_plan"]["case"]["lots"][0].update(federal_basis="100000", nj_basis="100000")
    plan["economics"]["long_multiple"] = "2"
    first = plan["calls"][0]
    first["amount"] = "50000"
    plan["observations"][1]["asset_return"] = "-1"
    if second_call:
        plan["calls"].append(
            dict(
                first,
                id="recapitalization",
                date="2027-02-28",
                recapitalization_units="50000",
                recapitalization_terms_assumed_confirmed=confirmed,
            )
        )
    return Scenario.model_validate(data)


def rising(financing="0", manager="0"):
    data = flat().model_dump(mode="json")
    plan = data["qoz_plan"]
    plan["economics"].update(
        long_multiple="2", annual_financing_rate=financing, annual_manager_fee=manager
    )
    first = plan["calls"][0]
    first["amount"] = "50000"
    plan["calls"].append(dict(first, id="second", date="2027-02-28"))
    plan["observations"][1]["asset_return"] = ".20"
    plan["observations"][2]["asset_return"] = ".10"
    return Scenario.model_validate(data)
