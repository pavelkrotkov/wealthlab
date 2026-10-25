"""Monthly conditional NAV, distributions, release and actual taxable basket disposal."""

from wealthlab.household.calendar import money
from wealthlab.products import exchange_fund_lots as lots
from wealthlab.products.exchange_fund_redemption import requested
from wealthlab.products.exchange_fund_trades import marked


def advance(ledger, observation, wallet):
    when = observation.date
    row = dict(
        date=when.isoformat(),
        fees=lots.ZERO,
        distribution=lots.ZERO,
        denied_redemptions=0,
        early_cash=lots.ZERO,
        basket_cash=lots.ZERO,
    )
    if ledger.active:
        grow(ledger, observation, row)
        distribute(ledger, observation, wallet, row)
    elif ledger.is_exchange:
        guard_closed(observation)
    events = execute_requests(ledger, observation, wallet, row)
    cash = sum(ledger.book.cash.values(), lots.ZERO)
    wallet.deposit(cash)
    ledger.book.cash = dict.fromkeys(ledger.book.cash, lots.ZERO)
    row["sale_cash"] = cash
    row["locked_value"] = ledger.nav if ledger.active else lots.ZERO
    row["federal_interest_basis"] = ledger.bases["federal"] if ledger.active else lots.ZERO
    row["nj_interest_basis"] = ledger.bases["nj"] if ledger.active else lots.ZERO
    row["account_value"] = marked(ledger.book, observation.prices) + row["locked_value"]
    wallet.balances[ledger.plan.account_id] = row["account_value"]
    ledger.prices = observation.prices
    ledger.log.append(row)
    return events


def grow(ledger, observation, row):
    """Mark the common benchmark, pay NAV fees and apply independently supplied tax bases.

    Basis adjustments do not create economic returns or household receipts.
    A supplied deduction cannot push outside basis below zero in this profile.
    """
    plan = ledger.plan

    def benchmark(prices):
        return sum(
            (
                b.value_weight * prices[b.security.id] / plan.opening_prices[b.security.id]
                for b in plan.basket
            ),
            lots.ZERO,
        )

    relative = benchmark(observation.prices) / benchmark(ledger.prices)
    # ponytail: supplied buy-and-hold benchmark; actual manager holdings remain unknown.
    ledger.nav = money(ledger.nav * relative)
    row["fees"] = min(ledger.nav, money(ledger.nav * plan.annual_fee / 12))
    ledger.nav -= row["fees"]
    ledger.bases["federal"] += observation.federal_basis_adjustment
    ledger.bases["nj"] += observation.nj_basis_adjustment
    if min(ledger.bases.values()) < 0:
        raise ValueError("Supplied basis adjustments cannot create negative partnership basis.")


def distribute(ledger, observation, wallet, row):
    amount = observation.distribution
    if amount > ledger.nav or amount > min(ledger.bases.values()):
        raise ValueError(
            "Distribution exceeds NAV or supplied adjusted basis; recognition missing."
        )
    ledger.nav -= amount
    for key in ledger.bases:
        ledger.bases[key] -= amount
    wallet.deposit(amount)
    row["distribution"] = amount


def guard_closed(observation):
    if any(
        (
            observation.distribution,
            observation.federal_basis_adjustment,
            observation.nj_basis_adjustment,
        )
    ):
        raise ValueError("Cash or basis changes after exchange exit require a settlement adapter.")


def execute_requests(ledger, observation, wallet, row):
    events = []
    for request in ledger.plan.requests:
        if request.date == observation.date:
            if observation.locked:
                row["denied_redemptions"] += 1
            else:
                events.extend(requested(ledger, request, observation.prices, wallet, row))
    return events
