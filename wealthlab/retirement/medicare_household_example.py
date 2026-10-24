"""Synthetic pre-benefit retirees see a conversion change IRMAA two years later."""

from datetime import date
from decimal import Decimal

from wealthlab.retirement.ira_household_example import synthetic as ira_example
from wealthlab.retirement.medicare_example import synthetic as premium_example
from wealthlab.retirement.medicare_household_inputs import MedicarePlan
from wealthlab.tax.projection_example import template as tax_template


def synthetic():
    case = ira_example()
    births = [date(1960, 10, 1), date(1961, 7, 1)]
    members = [
        p.model_copy(update=dict(birth_date=b)) for p, b in zip(case.members, births, strict=True)
    ]
    owners = [
        p.model_copy(update=dict(birth_date=b))
        for p, b in zip(case.ira_plan.owners, births, strict=True)
    ]
    accounts = [
        a.model_copy(update=dict(balance=Decimal(250000))) if a.wrapper == "cash" else a
        for a in case.accounts
    ]
    accounts[1] = accounts[1].model_copy(update=dict(balance=Decimal(500000)))
    orders = list(case.ira_plan.orders)
    orders[1] = orders[1].model_copy(update=dict(amount=Decimal(250000)))
    orders.append(orders[2].model_copy(update=dict(id="draw_2028", date=date(2028, 1, 1))))
    ira = case.ira_plan.model_copy(update=dict(owners=owners, orders=orders))
    case = case.model_copy(
        update=dict(
            name="Synthetic Roth conversion and Medicare lookback",
            end=date(2029, 1, 1),
            members=members,
            accounts=accounts,
            ira_plan=ira,
        )
    )
    return case.model_copy(
        update=dict(tax_plan=tax_template(case), medicare_plan=synthetic_plan(case))
    )


def synthetic_plan(scenario):
    payload = premium_example().model_dump(mode="json")
    mapping = dict(person=scenario.members[0].id, spouse=scenario.members[1].id)
    payload.update(
        start_year=scenario.start.year,
        end_year=scenario.end.year,
        opening_cash=0,
        receipts=[],
        income_policy="household_completed_returns",
    )
    for person in payload["members"]:
        person["id"] = mapping[person["id"]]
    for record in payload["income_history"]:
        record["members"] = [mapping[k] for k in record["members"]]
    for coverage in payload["coverage"]:
        coverage.update(member=mapping[coverage["member"]], end=scenario.end.isoformat())
    return MedicarePlan.model_validate(
        dict(
            case=payload,
            direct_billing_without_benefit_withholding_confirmed=True,
            costs_excluded_from_other_expenses_confirmed=True,
            complete_household_tax_history_confirmed=True,
        )
    )
