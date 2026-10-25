"""One existing long/short book owns the corporation assets, creditor debt and cash.

New equity repays existing loans before the same book retargets exposures.
All stock lots share its returns, costs, losses and eventual liquidation;
limited liability floors the shareholder value once, never once per call.
The preferred hurdle weights actual contribution dates and is not a payment.
"""

from datetime import timedelta
from decimal import Decimal

from wealthlab.household.calendar import money
from wealthlab.products.long_short_book import ZERO, deposit, equity, gross, opening
from wealthlab.products.long_short_margin import check
from wealthlab.products.long_short_step import advance
from wealthlab.products.long_short_trading import liquidate, rebalance, redeem


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
    book = opening(case)
    entry_cost = money(gross(book) * case.turnover_cost)
    entry = check(book, case, False)
    retain_cash(book)
    return dict(
        case=case,
        book=book,
        entry=entry,
        entry_cost=entry_cost,
        invested=when,
        funded=funded,
        contributions=[(when, funded)],
        dividends=ZERO,
        months=0,
        sold=False,
        receivable=ZERO,
        settlement=None,
    )


def step(fund, observation):
    book = fund["book"]
    values = dict(
        long_return=observation.asset_return,
        short_return=0,
        long_yield=0,
        short_yield=0,
        locked=observation.locked,
    )
    row = advance(book, fund["case"], values, observation.date, fund["months"], False)
    row.pop("entry_cost", None)  # Opening costs are dated in the actual subscription audit.
    fund["months"] += 1
    # The limited-liability shareholder cannot draw on entity debt or liquidation cash.
    retain_cash(book)
    return row


def distribute(fund, observation):
    requested = money(max(ZERO, equity(fund["book"])) * observation.dividend_fraction_of_nav)
    if not requested or observation.locked:
        return ZERO
    # This declared E&P cash dividend has no supplied investor stock-sale cost.
    paid = redeem(fund["book"], requested, ZERO)["redemption_paid"]
    fund["book"]["outside"] = ZERO
    fund["dividends"] += paid
    return paid


def sell(fund, plan, when):
    nav = max(ZERO, equity(fund["book"]))
    hurdle = sum(
        (
            amount * (1 + plan.preferred_hurdle * Decimal((when - date).days) / 365)
            for date, amount in fund["contributions"]
        ),
        ZERO,
    )
    result = liquidate(fund["book"], fund["case"].exit_cost)
    cash = result["liquidation_cash"]
    carry = min(cash, money(max(ZERO, cash + fund["dividends"] - hurdle) * plan.carry_fraction))
    if plan.mode == "liquid_reference":
        carry = ZERO
    proceeds = result["liquidation_cash"] - carry
    fund["book"]["outside"] = ZERO
    fund.update(sold=True, receivable=proceeds, settlement=settlement(when, plan.settlement_months))
    return dict(
        fmv=nav - carry,
        proceeds=proceeds,
        carry=carry,
        preferred_hurdle_threshold=money(hurdle),
        **result,
    )


def settlement(when, delay):
    index = when.year * 12 + when.month - 1 + delay + 1
    return when.replace(year=index // 12, month=index % 12 + 1, day=1) - timedelta(days=1)


def value(fund):
    return fund["receivable"] + (ZERO if fund["sold"] else max(ZERO, equity(fund["book"])))


def subscribe(fund, funded, when):
    """Actual new equity first cures creditor debt, then resets the supplied target exposure."""
    before = equity(fund["book"])
    deposit(fund["book"], funded)
    fund["funded"] += funded
    fund["contributions"].append((when, funded))
    result = {}
    if equity(fund["book"]) > 0:
        fund["book"]["closed"] = False
        result = rebalance(fund["book"], fund["case"])
    result.update(check(fund["book"], fund["case"], False))
    retain_cash(fund["book"])
    return dict(
        opening_entity_equity=before,
        cash_contributed=funded,
        closing_entity_equity=equity(fund["book"]),
        **result,
    )


def retain_cash(book):
    book["cash"] += book["outside"]
    book["outside"] = ZERO
