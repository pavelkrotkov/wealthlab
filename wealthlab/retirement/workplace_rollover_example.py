"""Original two-year source-to-IRA example with no assumed transferred plan basis.

The55-year-old separates with100k, rolls80k into a10k IRA, and then draws15k.
The source plan's age55 exception does not exempt this IRA withdrawal's1.5k tax.
"""

from wealthlab.household.scenario import Scenario
from wealthlab.retirement.ira_household_example import template as ira_template
from wealthlab.retirement.workplace_withdrawal_example import synthetic as workplace
from wealthlab.tax.projection_example import template as tax_template


def synthetic():
    data = workplace().model_dump(mode="json")
    data.update(name="Synthetic actual plan-to-IRA rollover", hsa_plan=None, expenses=[])
    data["accounts"] = [a for a in data["accounts"] if a["id"] in {"cash", "work_pretax"}]
    data["accounts"][0]["balance"] = 10000
    data["accounts"].append(
        dict(
            id="ira",
            owner="person_a",
            wrapper="traditional",
            balance=10000,
            currency="USD",
            monthly_fee=0,
            provenance="illustration",
        )
    )
    cash = data["workplace_plan"]["cash_withdrawals"]
    cash["orders"] = []
    cash["direct_rollovers"] = [order()]
    scenario = Scenario.model_validate(data)
    plan = ira_template(scenario).model_dump(mode="json")
    plan.update(
        complete_ordinary_ira_pools_confirmed=True,
        other_tax_inputs_exclude_ira_events_confirmed=True,
        orders=[
            dict(
                id="ira_draw",
                provenance="illustration",
                date="2026-03-01",
                source="ira",
                kind="withdrawal",
                amount=15000,
                early_penalty_exception=False,
            )
        ],
    )
    data["ira_plan"] = plan
    data["tax_plan"] = tax_template(scenario).model_dump(mode="json")
    return Scenario.model_validate(data)


def order():
    return dict(
        id="direct_transfer",
        provenance="illustration",
        date="2026-02-01",
        source="work_pretax",
        destination="ira",
        amount=80000,
        eligible_direct_cash_rollover_to_same_owner_ordinary_ira_confirmed=True,
    )
