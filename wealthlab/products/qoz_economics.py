"""Reuse the existing private-fund internal long/short book, one book per funded call."""

from datetime import timedelta
from decimal import Decimal

from wealthlab.household.calendar import money
from wealthlab.products.long_short_book import ZERO, equity, opening
from wealthlab.products.long_short_step import advance
from wealthlab.products.long_short_trading import liquidate, redeem


def create(plan, funded, when):
    case = plan.economics.model_copy(update=dict(opening_equity=funded))
    if plan.mode == "liquid_reference":
        case = case.model_copy(
            update=dict(
                long_multiple=Decimal(1),
                annual_manager_fee=ZERO,
                annual_financing_rate=ZERO,
                turnover_cost=ZERO,
                exit_cost=ZERO,
                maintenance_fraction_of_gross=ZERO,
            )
        )
    return dict(
        case=case,
        book=opening(case),
        invested=when,
        funded=funded,
        dividends=ZERO,
        months=0,
        sold=False,
        receivable=ZERO,
        settlement=None,
    )


def step(tranche, observation):
    book = tranche["book"]
    values = dict(
        long_return=observation.asset_return,
        short_return=0,
        long_yield=0,
        short_yield=0,
        locked=observation.locked,
    )
    row = advance(book, tranche["case"], values, observation.date, tranche["months"], False)
    tranche["months"] += 1
    # The limited-liability shareholder cannot draw on entity debt or liquidation cash.
    book["cash"] += book["outside"]
    book["outside"] = ZERO
    return row


def distribute(tranche, observation):
    requested = money(max(ZERO, equity(tranche["book"])) * observation.dividend_fraction_of_nav)
    if not requested or observation.locked:
        return ZERO
    paid = redeem(tranche["book"], requested, tranche["case"].exit_cost)["redemption_paid"]
    tranche["book"]["outside"] = ZERO
    tranche["dividends"] += paid
    return paid


def sell(tranche, plan, when):
    nav = max(ZERO, equity(tranche["book"]))
    elapsed = Decimal((when - tranche["invested"]).days) / Decimal(365)
    hurdle = tranche["funded"] * (1 + plan.preferred_hurdle * elapsed)
    carry = min(nav, money(max(ZERO, nav + tranche["dividends"] - hurdle) * plan.carry_fraction))
    if plan.mode == "liquid_reference":
        carry = ZERO
    result = liquidate(tranche["book"], tranche["case"].exit_cost)
    carry = min(result["liquidation_cash"], carry)
    proceeds = result["liquidation_cash"] - carry
    tranche["book"]["outside"] = ZERO
    tranche.update(
        sold=True, receivable=proceeds, settlement=settlement(when, plan.settlement_months)
    )
    return dict(fmv=nav - carry, proceeds=proceeds, carry=carry, **result)


def settlement(when, delay):
    index = when.year * 12 + when.month - 1 + delay + 1
    return when.replace(year=index // 12, month=index % 12 + 1, day=1) - timedelta(days=1)


def value(tranche):
    return tranche["receivable"] + (ZERO if tranche["sold"] else max(ZERO, equity(tranche["book"])))
