"""Complete synthetic paths share opening capital and independently stated insurance need.

These educational values are not an insurer forecast. Each1000premium adds900
to supplied surrender value, so the flat cash identity loses100per actual premium.
No illustration value, death benefit or tax classification is inferred or scaled.
"""

from datetime import date
from decimal import Decimal

from wealthlab.optimization.inputs import PolicySearch
from wealthlab.optimization.product_example import account
from wealthlab.optimization.product_example_terms import insurance
from wealthlab.products.life_household_example import event
from wealthlab.products.life_household_inputs import LifeHolding


def extend(case):
    if not case.household.synthetic:
        raise ValueError("The life-path starter only extends synthetic examples.")
    data = case.model_dump(mode="json")
    if data["household"]["life_plan"] is None:
        data["household"]["accounts"].append(account("life_policy", "insurance"))
        data["household"]["life_plan"] = insurance(case.household)
    baseline = LifeHolding.model_validate(data["household"]["life_plan"]["holdings"][0]).model_dump(
        mode="json"
    )
    names = ("paid_up", "one_premium", "two_premiums")
    data["life_opportunities"] = [
        path(baseline, identity, count) for count, identity in enumerate(names)
    ]
    data["dimensions"].append(
        dict(
            id="policy_funding",
            choices=[dict(id=name, life_paths={baseline["account_id"]: name}) for name in names],
        )
    )
    return PolicySearch.model_validate(data)


def path(baseline, identity, count):
    from copy import deepcopy

    holding = deepcopy(baseline)
    contract = holding["contract"]
    dates = [date(2026, 1, 15), date(2027, 1, 15)][:count]
    terminal = contract["events"][-1]
    terminal["amount"] = str(10000 + 900 * count)
    premiums = [
        event(f"premium_{i}", when.isoformat(), "premium", 1000) for i, when in enumerate(dates)
    ]
    contract.update(
        name="Synthetic " + identity,
        source="Complete synthetic conditional path: each1000premium adds900surrender value",
        events=[*premiums, terminal],
        stop_funding_date=dates[-1].isoformat() if dates else contract["start"],
    )
    for value in contract["values"]:
        amount = Decimal(
            10000 + 900 * sum(when <= date.fromisoformat(value["date"]) for when in dates)
        )
        value["gross_cash_value"] = value["gross_surrender_value"] = str(amount)
    holding["failure_exits"] = {
        premium["id"]: dict(
            event=event(premium["id"] + "_failed", premium["date"], "surrender", 10000 + 900 * i),
            source="Synthetic full settlement if this premium cannot be paid",
            applicable_to_unfunded_payment_confirmed=True,
        )
        for i, premium in enumerate(premiums)
    }
    return dict(
        id=identity,
        provenance="illustration",
        holding=holding,
        matched_path_terms_assumed_confirmed=True,
        explanation="Independent complete policy illustration for the chosen premium schedule",
    )
