"""Original source-matched retirement/vesting profiles, never inferred from common ownership.

Both choices retain320000 vested opening wealth and80000 contingent value.
Source events explicitly forfeit that contingency on early retirement or vest
and distribute it after another year of work. No actuarial/legal rule is inferred.
"""

from copy import deepcopy

from wealthlab.employment.compensation_termination_example import terminated
from wealthlab.markets.example import asset
from wealthlab.optimization.contract_example import employer_binding
from wealthlab.optimization.example import synthetic as base
from wealthlab.optimization.inputs import PolicySearch
from wealthlab.optimization.product_example import add_factor


def synthetic():
    data = base().model_dump(mode="json")
    household = data["household"]
    household["name"] = "Synthetic source-matched retirement and employer vesting"
    source = terminated().model_dump(mode="json")
    household["accounts"].append(next(a for a in source["accounts"] if a["id"] == "employer_fund"))
    household["employment_plan"] = work(household, "2027-01-01")
    household["compensation_plan"] = contract(source["compensation_plan"], "2027-01-01", True)
    data["binding"]["employers"] = [employer_binding()]
    data["employment_offers"] = [
        offer(household, when, later, source["compensation_plan"])
        for when, later in (("2026-01-01", False), ("2027-01-01", True))
    ]
    data["dimensions"] = [
        dict(
            id="employment_retirement",
            choices=[
                dict(id=p["id"], retirement_dates=p["retirement_dates"], employment_offer=p["id"])
                for p in data["employment_offers"]
            ],
        )
    ]
    for market in (data["training"], data["validation"]):
        add_factor(market, asset("employer", "employer", 0.04, 0.35, 0))
    return PolicySearch.model_validate(data)


def work(household, when):
    return dict(
        paths=[
            dict(
                id="current_work",
                provenance="illustration",
                owner=household["members"][0]["id"],
                income_ids=[household["incomes"][0]["id"]],
                opening_multiplier="1",
                changes=[
                    dict(
                        id="leave_work",
                        provenance="illustration",
                        date=when,
                        kind="job_loss",
                        multiplier="0",
                    )
                ],
            )
        ]
    )


def contract(original, when, later):
    plan = deepcopy(original)
    events = {event["id"]: event for event in plan["events"]}
    for event in events.values():
        event["date"] = when
    if later:
        events["forfeit"].update(id="vest", kind="vest", sequence=0)
        events["redeem"].update(sequence=1, amount="100000")
        events["exit_tax"].update(
            federal=dict(allowed_passive_income="100000"),
            new_jersey=dict(business=dict(partnership="100000")),
        )
    events["termination"]["source_date"] = when
    plan["events"] = list(events.values())
    return plan


def offer(household, when, later, original):
    dates = {m["id"]: m["retirement_date"] for m in household["members"]}
    dates[household["members"][0]["id"]] = when
    return dict(
        id="later" if later else "early",
        provenance="illustration",
        source="Original hypothetical employment and award worksheet; no actual plan claim",
        source_date=household["start"],
        available_on=household["start"],
        retirement_dates=dates,
        employment_plan=work(household, when),
        compensation_plan=contract(original, when, later),
        all_candidate_income_and_market_paths_confirmed=True,
        complete_cash_tax_vesting_forfeiture_and_exit_facts_confirmed=True,
    )
