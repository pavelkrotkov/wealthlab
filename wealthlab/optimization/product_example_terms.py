"""Complete illustrative exits reuse native product terms and their actual cash ledgers.

These short contracts deliberately differ from commercial product terms. The
exchange liquidity date, zero supplied allocations and constant policy values
are explicit educational assumptions, not eligibility or return forecasts.
"""

from datetime import date, timedelta

from wealthlab.household.calendar import months
from wealthlab.products.exchange_fund_example import observations as exchange_marks
from wealthlab.products.exchange_fund_example import request
from wealthlab.products.exchange_fund_example import synthetic as exchange_case
from wealthlab.products.household_example import observations
from wealthlab.products.life_household_example import event, holding
from wealthlab.products.long_short_example import terms
from wealthlab.products.private_fund_example import contract


def sleeve(scenario, factor, private):
    identity = "private_fund" if private else "margin_sleeve"
    case = terms().model_dump(mode="json")
    case.update(
        opening_equity="10000",
        outside_cash="0",
        long_factor=factor,
        short_factor=factor,
        exit_at_horizon=not private,
        margin_policy="liquidate_on_breach",
    )
    fund = contract() if private else None
    if fund:
        fund["requests"][0]["notice_date"] = "2027-07-01"
        fund.update(
            federal_opening_basis="10000", new_jersey_opening_basis="10000", basis_adjustments=[]
        )
    marks = observations(scenario)
    for mark in marks:
        mark["id"] = identity + "_" + mark["id"]
    return dict(
        id=identity + "_book",
        provenance="illustration",
        account_id=identity,
        case=case,
        private_fund_contract=fund,
        observations=marks,
        allocations=[],
        all_tax_recognition_and_exit_assumptions_supplied_confirmed=True,
    )


def exchange(scenario):
    plan = exchange_case().exchange_fund_plan.model_dump(mode="json")
    plan.update(
        contribution_quantity="100",
        liquid_after="2027-01-01",
        observations=exchange_marks(scenario),
    )
    plan["source_lot"].update(quantity="100", federal_basis="10000", nj_basis="10000")
    plan["requests"] = [
        request("release", date(2027, 1, 31), "redeem"),
        request("exchange_exit", scenario.end - timedelta(days=1), "sell_liquid"),
    ]
    return plan


def insurance(scenario):
    policy = holding()
    policy.update(failure_exits={}, payments_complete_through="2031-01-01")
    policy["contract"].update(
        events=[event("life_exit", scenario.end - timedelta(days=1), "surrender", 10000)],
        values=[
            dict(
                date=end - timedelta(days=1),
                gross_cash_value="10000",
                gross_surrender_value="10000",
                gross_death_benefit="100000",
            )
            for _, end in months(scenario.start, scenario.end)
            if end < scenario.end
        ],
    )
    return dict(holdings=[policy], insurance_need_by_owner={"person_a": "0"})
