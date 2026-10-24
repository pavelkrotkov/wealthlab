"""Replay the reference's IRA policy through real cash, separate basis and annual tax books."""

from datetime import date
from decimal import ROUND_DOWN, Decimal

from wealthlab.household.calendar import money
from wealthlab.household.example import synthetic
from wealthlab.household.scenario import Scenario
from wealthlab.retirement.distribution_inputs import WithdrawalOrder
from wealthlab.retirement.ira_household_example import template as ira_template
from wealthlab.tax.projection_example import template as tax_template


def compile_case(case, reference):
    start, end = f"{case.start_year}-01-01", f"{case.start_year + case.years}-01-01"
    data = synthetic().model_dump(mode="json")
    member = dict(
        data["members"][0], birth_date=f"{case.start_year - case.age}-07-01", retirement_date=start
    )
    data.update(
        name="OWL policy through actual household retirement ledger",
        synthetic=case.synthetic,
        start=start,
        end=end,
        members=[member],
        incomes=[],
        debts=[],
        contributions=[],
        inflation=0,
        usd_per_currency=dict(USD=1),
        reserve_years=0,
        target_age=case.age + case.years - 1,
        accounts=[
            account(member["id"], key, wrapper, balance)
            for key, wrapper, balance in (
                ("cash", "cash", case.cash),
                ("retirement", "traditional", case.traditional_ira),
                ("roth", "roth", case.roth_ira),
            )
        ],
        expenses=expenses(case, start, end),
    )
    scenario = Scenario.model_validate(data)
    ira = ira_template(scenario)
    owner = ira.owners[0].model_copy(
        update=dict(
            nj_ira_basis=case.nj_ira_basis,
            birth_1959_start_age=case.birth_1959_start_age,
            roth_first_year=case.roth_first_year,
        )
    )
    ira = ira.model_copy(
        update=dict(
            owners=[owner],
            orders=orders(reference),
            complete_ordinary_ira_pools_confirmed=True,
            other_tax_inputs_exclude_ira_events_confirmed=True,
        )
    )
    return scenario.model_copy(update=dict(ira_plan=ira, tax_plan=taxes(scenario)))


def taxes(scenario):
    plan = tax_template(scenario)
    cases = [
        c.model_copy(update=dict(policy=c.policy.model_copy(update=dict(mode="package_law"))))
        for c in plan.cases
    ]
    return plan.model_copy(update=dict(cases=cases))


def account(owner, key, wrapper, balance):
    return dict(
        id=key,
        provenance="assumption",
        owner=owner,
        currency="USD",
        wrapper=wrapper,
        balance=str(balance),
        monthly_fee="0",
    )


def orders(reference):
    return [
        WithdrawalOrder.model_validate(
            dict(
                id=f"{key}_{year}",
                provenance="assumption",
                date=date(year, 1, 1),
                source=key,
                destination=None,
                kind="withdrawal",
                amount=money(Decimal(str(reference["withdrawals"][0][j][n]))),
                early_penalty_exception=False,
            )
        )
        for n, year in enumerate(reference["years"])
        for key, j in (("retirement", 1), ("roth", 2))
        if money(Decimal(str(reference["withdrawals"][0][j][n]))) > 0
    ]


def expenses(case, start, end):
    monthly = (case.annual_spending / 12).quantize(Decimal(".01"), rounding=ROUND_DOWN)
    extra = case.annual_spending - monthly * 12
    values = [expense("spending", start, end, monthly)]
    if extra:
        values.extend(
            expense(f"december_{year}", f"{year}-12-01", f"{year + 1}-01-01", extra)
            for year in range(case.start_year, case.start_year + case.years)
        )
    return values


def expense(key, start, end, amount):
    return dict(
        id=key,
        provenance="assumption",
        start=start,
        end=end,
        monthly_amount=str(amount),
        currency="USD",
        annual_growth=0,
        category="essential",
    )
