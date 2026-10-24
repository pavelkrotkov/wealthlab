"""A synthetic fixed two-year IRA funding case, never a personal withdrawal recommendation."""

from datetime import date
from decimal import Decimal

from wealthlab.household.example import synthetic as household
from wealthlab.household.records import Account
from wealthlab.retirement.distribution_inputs import DistributionOwner, WithdrawalOrder
from wealthlab.retirement.ira_household_inputs import IRAPlan
from wealthlab.tax.projection_example import template as tax_template


def synthetic():
    case = household()
    members = [p.model_copy(update=dict(retirement_date=case.start)) for p in case.members]
    roth = Account(
        id="roth",
        provenance="illustration",
        owner="person_a",
        currency="USD",
        wrapper="roth",
        balance=0,
        monthly_fee=0,
    )
    cash = case.accounts[0].model_copy(update=dict(balance=Decimal("100000")))
    case = case.model_copy(
        update=dict(
            name="Synthetic IRA withdrawals and conversion",
            members=members,
            accounts=[cash, case.accounts[1], roth],
            incomes=[],
        )
    )
    plan = template(case, orders()).model_copy(
        update=dict(
            complete_ordinary_ira_pools_confirmed=True,
            other_tax_inputs_exclude_ira_events_confirmed=True,
        )
    )
    return case.model_copy(update=dict(tax_plan=tax_template(case), ira_plan=plan))


def template(scenario, orders=None):
    owners = [
        DistributionOwner(
            id=p.id,
            provenance="assumption",
            birth_date=p.birth_date,
            federal_ira_basis=0,
            nj_ira_basis=0,
            roth_regular_basis=0,
            nj_roth_basis=0,
            roth_first_year=None,
            rmd_table="uniform",
        )
        for p in scenario.members
    ]
    return IRAPlan(
        owners=owners,
        products={
            a.id: ("traditional_ira" if a.wrapper == "traditional" else "roth_ira")
            for a in scenario.accounts
            if a.wrapper in {"traditional", "roth"}
        },
        orders=[] if orders is None else orders,
        returns=[],
        complete_ordinary_ira_pools_confirmed=False,
        other_tax_inputs_exclude_ira_events_confirmed=False,
        reconciliation="year_end_fixed_schedule",
    )


def orders():
    return [
        WithdrawalOrder.model_validate(
            dict(
                id=key,
                provenance="illustration",
                date=date.fromisoformat(when),
                source="retirement",
                destination=target,
                kind=kind,
                amount=amount,
                early_penalty_exception=False,
            )
        )
        for key, when, target, kind, amount in [
            ("draw_2026", "2026-01-01", None, "withdrawal", 20000),
            ("convert_2026", "2026-07-01", "roth", "conversion", 10000),
            ("draw_2027", "2027-01-01", None, "withdrawal", 20000),
        ]
    ]
