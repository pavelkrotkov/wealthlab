"""A separately supplied delayed-premium path has no free earlier coverage."""

from tests.test_life_allocation_failures import cash_case
from wealthlab.household.projection import project
from wealthlab.household.scenario import Scenario


def test_supplied_delayed_issue_path_has_no_protection_before_the_actual_premium():
    data = cash_case(10000)
    h = data["life_plan"]["holdings"][0]
    c = h["contract"]
    c["events"] = c["events"][1:]
    c["events"][-1].update(amount="1100")
    c["values"][0].update(gross_cash_value="0", gross_surrender_value="0", gross_death_benefit="0")
    c["values"][1].update(gross_cash_value="900", gross_surrender_value="900")
    h["failure_exits"] = {"new_premium2": h["failure_exits"]["new_premium1"]}
    h["failure_exits"]["new_premium2"]["event"].update(date="2026-02-15")
    rows = project(Scenario.model_validate(data))
    assert [r["life_net_death_benefit"] for r in rows] == [0, 100000, 0]
    assert [r["life_premiums_paid"] for r in rows] == [0, 1000, 0]
    assert [r["closing_cash"] for r in rows] == [10000, 9000, 10100]
