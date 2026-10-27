"""Both allowed IRA schedules use actual conversion clocks and preserve capital once."""

from optimization_cases import flat

from wealthlab.household.scenario import Scenario
from wealthlab.optimization.inputs import PolicySearch
from wealthlab.optimization.search import search
from wealthlab.retirement.ira_household_example import template


def order(identity, kind, source, destination, month):
    return dict(
        id=identity,
        provenance="illustration",
        date=f"2026-{month}-01",
        kind=kind,
        source=source,
        destination=destination,
        amount="10000",
        early_penalty_exception=False,
    )


def ira_case():
    data = flat().model_dump(mode="json")
    household = data["household"]
    common = dict(owner="person_a", provenance="illustration", currency="USD", monthly_fee="0")
    household["accounts"] += [
        dict(common, id="ira", wrapper="traditional", balance="10000"),
        dict(common, id="roth", wrapper="roth", balance="0"),
    ]
    plan = template(Scenario.model_validate(household)).model_dump(mode="json")
    plan.update(
        complete_ordinary_ira_pools_confirmed=True,
        other_tax_inputs_exclude_ira_events_confirmed=True,
    )
    plan["owners"][0]["roth_first_year"] = 2020
    household["ira_plan"] = plan
    data["dimensions"][0]["locked_choice"] = "early"
    data["dimensions"].append(
        dict(
            id="ira_schedule",
            choices=[
                dict(id="direct", ira_orders=[order("draw", "withdrawal", "ira", None, "01")]),
                dict(
                    id="conversion",
                    ira_orders=[
                        order("convert", "conversion", "ira", "roth", "01"),
                        order("roth_draw", "withdrawal", "roth", None, "12"),
                    ],
                ),
            ],
        )
    )
    return PolicySearch.model_validate(data)


def test_conversion_then_young_roth_draw_does_not_hide_recapture_or_duplicate_assets():
    result = search(ira_case())
    assert result["evaluated_candidates"] == 2
    assert [c["median_real_after_tax_exit_wealth"] for c in result["candidates"]] == [
        260999,
        260999,
    ]
    assert [c["median_net_cash_tax"] for c in result["candidates"]] == [1000, 1000]
