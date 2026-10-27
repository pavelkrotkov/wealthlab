"""Buy a complete supplied synthetic new-policy path using existing household cash.

The policy starts with zero value/basis/debt. The zero need is an explicit
educational baseline, never inferred from financial wealth or a selected exit.
No insurer illustration is scaled or extended beyond its supplied terminal event.
"""

from wealthlab.optimization.inputs import PolicySearch
from wealthlab.products.life_allocation_example import holding
from wealthlab.products.life_household_calendar import reserve_end


def extend(case):
    if not case.household.synthetic:
        raise ValueError("The new-policy starter only extends synthetic examples.")
    if case.new_life_opportunities:
        raise ValueError("The new-policy starter cannot replace existing supplied offers.")
    data = case.model_dump(mode="json")
    household = data["household"]
    owner = case.household.members[0].id
    if household["life_plan"] is None:
        household["life_plan"] = dict(holdings=[], insurance_need_by_owner={owner: "0"})
    quote = holding()
    quote["payments_complete_through"] = reserve_end(
        case.household.end, case.targets.reserve_years
    ).isoformat()
    data["new_life_opportunities"] = [
        dict(
            id="new_policy",
            provenance="illustration",
            owner=owner,
            holding=quote,
            matched_new_issue_terms_confirmed=True,
            source="Original complete synthetic new issue; no actual insurer quote",
        )
    ]
    data["dimensions"].append(
        dict(
            id="new_policy_purchase",
            choices=[
                dict(id="no_new_policy", new_life_purchases=[]),
                dict(id="supplied_policy", new_life_purchases=["new_policy"]),
            ],
        )
    )
    return PolicySearch.model_validate(data)
