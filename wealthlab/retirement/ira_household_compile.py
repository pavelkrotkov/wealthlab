"""Reconcile locked annual schedules without feeding future basis into earlier decisions.

The existing IRA engine owns cash chronology, annual basis, Roth clocks and
RMD checks. Only the completed annual taxable result enters December's tax
ledger. In-year tax estimates remain explicitly supplied household payments.
"""

from wealthlab.retirement.account_liquidity import annual as annual_locks
from wealthlab.retirement.distribution_inputs import DistributionCase, DistributionOwner, IRAAccount
from wealthlab.retirement.distributions import run
from wealthlab.retirement.ira_household_validation import validate


def compile_years(scenario):
    validate(scenario)
    plan = scenario.ira_plan
    owners = plan.owners
    accounts = opening_accounts(scenario)
    results = []
    for year in range(scenario.start.year, scenario.end.year):
        case = annual_case(plan, owners, accounts, year)
        result = run(case)
        results.append(result)
        owners = carry_owners(owners, result)
        accounts = [
            a.model_copy(update=dict(balance=result["account_balances"][a.id])) for a in accounts
        ]
    return results


def carry_owners(owners, result):
    ending = {p["owner"]: p for p in result["owners"]}
    fields = set(DistributionOwner.model_fields)
    return [
        DistributionOwner.model_validate(
            dict(
                **p.model_dump(exclude=fields & set(ending[p.id])),
                **{k: v for k, v in ending[p.id].items() if k in fields},
            )
        )
        for p in owners
    ]


def opening_accounts(scenario):
    products = scenario.ira_plan.products
    return [
        IRAAccount.model_validate(dict(**a.model_dump(), product=products[a.id]))
        for a in scenario.accounts
        if a.id in products
    ]


def annual_case(plan, owners, accounts, year):
    return DistributionCase(
        year=year,
        opening_cash=0,
        opening_context_complete=True,
        owners=owners,
        accounts=accounts,
        nj_treatment="resident_combined_owner_pools",
        rmd_policy="december_target_no_deferral",
        orders=[e for e in plan.orders if e.date.year == year],
        returns=[e for e in plan.returns if e.date.year == year],
        liquidity_locks=annual_locks(plan.liquidity_locks, year),
    )
