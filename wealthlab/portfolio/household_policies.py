"""Dated month-end policies use live household marks and the existing trade engines.

Sales and replacement pairs execute before the single cash sweep and tax
recognition. Unlinked household assets remain in pre-tax concentration wealth;
otherwise sweeping sale cash out of the book would falsely reset its stock
weight to 100 percent. Taxes and later spending can change the final weight.
"""

from datetime import date, timedelta
from decimal import Decimal

from wealthlab.portfolio.harvesting import execute as harvest
from wealthlab.portfolio.policy_execution import execute as sell


def validate(case):
    policies = [*case.sale_policies, *case.harvest_policies]
    if any(p.date != month_end(p.date) for p in policies):
        raise ValueError("Household sale/harvest policies require month-end decision dates.")
    if any(p.mode == "tax_budget" for p in case.sale_policies):
        raise ValueError("Household tax-budget decisions require a dated annual-forecast adapter.")


def month_end(when):
    following = date(when.year + when.month // 12, when.month % 12 + 1, 1)
    return following - timedelta(days=1)


def execute(lots, wallet, start, end):
    lots.book.external_wealth = sum(
        (
            value
            for identity, value in wallet.balances.items()
            if identity not in lots.book.accounts
        ),
        Decimal(0),
    )
    for policy in lots.case.sale_policies:
        if start <= policy.date < end:
            decision = sale(lots, policy)
            lots.sale_decisions.append(decision)
    for policy in lots.case.harvest_policies:
        if start <= policy.date < end:
            records = harvesting(lots, policy)
            lots.book.harvest_decisions.extend(records)


def sale(lots, policy):
    if policy.security_id in lots.locked:
        return dict(
            policy=policy.id,
            date=policy.date.isoformat(),
            mode=policy.mode,
            status="blocked by market liquidity lock",
            sold_units=Decimal(0),
        )
    return sell(lots.case, lots.book, policy.model_copy(update=dict(prices=dict(lots.prices))))


def harvesting(lots, policy):
    if {policy.security_id, policy.replacement_id} & lots.locked:
        return [
            dict(
                policy=policy.id,
                date=policy.date.isoformat(),
                status="source or replacement blocked by market liquidity lock",
            )
        ]
    return harvest(lots.book, policy.model_copy(update=dict(prices=dict(lots.prices))))
