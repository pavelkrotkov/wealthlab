"""Complete separate-plan RMD context with an initially empty ordinary IRA destination."""

from wealthlab.household.scenario import Scenario
from wealthlab.retirement.ira_household_example import template
from wealthlab.retirement.workplace_rmd_example import account, synthetic
from wealthlab.retirement.workplace_rollover_example import order


def rmd_data():
    data = synthetic().model_dump(mode="json")
    data["accounts"].append(account("ira", "traditional", 0))
    plan = template(Scenario.model_validate(data)).model_dump(mode="json")
    plan.update(
        complete_ordinary_ira_pools_confirmed=True,
        other_tax_inputs_exclude_ira_events_confirmed=True,
    )
    data["ira_plan"] = plan
    return data


def transfer(identity, source, when):
    return dict(order(), id=identity, source=source, date=when, amount=100000)
