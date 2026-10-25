"""Original short demonstration; supplied policy values are not insurer illustrations.

The limited and longer schedules use different expressly supplied cash values.
Term protection is priced independently at $100 per month and has no cash value.
Every branch starts with the same $10,000 household capital and $1,000 bills.
"""

from copy import deepcopy

from wealthlab.household.scenario import Scenario
from wealthlab.portfolio.saving_example import synthetic as saving_household
from wealthlab.products.life_comparison_inputs import LifeComparison
from wealthlab.products.life_household_example import event, holding


def account(identity):
    return dict(
        id=identity,
        provenance="assumption",
        owner="person_a",
        currency="USD",
        wrapper="insurance",
        balance="0",
        monthly_fee="0",
    )


def limited():
    data = saving_household().model_dump(mode="json")
    data["name"] = "Limited premium schedule"
    data["accounts"][0]["balance"] = "10000"
    data["accounts"].append(account("life_policy"))
    data["lot_plan"]["savings"] = []
    h = holding()
    h["opening_values"].update(gross_cash_value="0", gross_surrender_value="0")
    c = h["contract"]
    c.update(opening_federal_basis="0", issue_date="2026-01-01", stop_funding_date="2026-02-15")
    c["events"] = c["events"][:3]
    c["events"][2]["cash_value_before"] = "2000"
    for value, amount in zip(c["values"], (900, 1800, 2000), strict=True):
        value.update(gross_cash_value=str(amount), gross_surrender_value=str(amount))
    h["failure_exits"]["premium1"]["event"]["amount"] = "0"
    h["failure_exits"]["premium2"]["event"]["amount"] = "900"
    data["life_plan"] = dict(holdings=[h], insurance_need_by_owner={"person_a": "150000"})
    return data


def longer(data):
    data = deepcopy(data)
    data["name"] = "Longer premium schedule"
    h = data["life_plan"]["holdings"][0]
    c = h["contract"]
    c["stop_funding_date"] = None
    c["events"] = [
        *c["events"][:2],
        event("premium3", "2026-03-15", "premium", 1000),
        event("future1", "2027-01-15", "premium", 1000),
        event("future2", "2028-01-15", "premium", 1000),
    ]
    c["values"][-1].update(gross_cash_value="2700", gross_surrender_value="2700")
    h["failure_exits"]["premium3"] = dict(
        h["failure_exits"]["premium2"],
        event=event("premium3_exit", "2026-03-15", "surrender", 1800),
    )
    return data


def term_reference(data):
    data = deepcopy(data)
    data["name"] = "Liquid saving plus separately priced term"
    data["accounts"][-1] = account("term")
    h = data["life_plan"]["holdings"][0]
    h["account_id"] = "term"
    h["opening_values"]["gross_death_benefit"] = "150000"
    c = h["contract"]
    c.update(
        name="Synthetic priced term coverage",
        source="Independent synthetic term price",
        stop_funding_date=None,
    )
    c["events"] = [
        event(f"term_{year}_{month}", f"{year}-{month:02d}-15", "premium", 100)
        for year in (2026, 2027, 2028)
        for month in range(1, 13)
    ]
    for value in c["values"]:
        value.update(gross_cash_value="0", gross_surrender_value="0", gross_death_benefit="150000")
    h["failure_exits"] = {
        e["id"]: dict(
            source="Synthetic termination with no value after unpaid term premium",
            applicable_to_unfunded_payment_confirmed=True,
            event=event(e["id"] + "_exit", e["date"], "lapse", 0),
        )
        for e in c["events"][:3]
    }
    savings = saving_household().model_dump(mode="json")["lot_plan"]["savings"][:2]
    for saving in savings:
        saving["amount"] = "900"
    data["lot_plan"]["savings"] = savings
    return data


def synthetic():
    first = limited()
    alternatives = {
        name: Scenario.model_validate(data)
        for name, data in (
            ("limited", first),
            ("longer", longer(first)),
            ("liquid_term", term_reference(first)),
        )
    }
    return LifeComparison(
        alternatives=alternatives,
        liquid_reference="liquid_term",
        term_account_ids=["term"],
        independently_priced_protection_confirmed=True,
    )
