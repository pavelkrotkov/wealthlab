"""Observed source sale closes before a next-year actual investment, without future cash."""

from qoz_cases import flat

from wealthlab.household.scenario import Scenario


def transition():
    data = flat(2026, 2).model_dump(mode="json")
    data["lot_plan"]["case"]["trades"][0]["date"] = "2026-12-15"
    data["qoz_plan"]["calls"][0]["date"] = "2027-01-31"
    data["qoz_plan"]["prior_source_year_revision_assumed_confirmed"] = True
    # Keep the interest locked through the supplied horizon, avoiding early reinclusion.
    for row in data["qoz_plan"]["observations"][-2:]:
        row["locked"] = True
    return Scenario.model_validate(data)
