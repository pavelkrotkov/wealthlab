"""Solve actual lot-sale cash and its taxes using copied trials of the same book.

Only configured liquid shares can be sold. The trial includes the same lot
selection, commission, partial-basis allocation and wash recognition as the
commit. Microshare rounding can leave extra cents; this is feasible funding,
not a claim of minimum tax or globally optimal liquidation.
"""

from copy import deepcopy
from decimal import ROUND_UP, Decimal

from wealthlab.household.calendar import money
from wealthlab.portfolio import household_recognition as recognition
from wealthlab.portfolio.generated_orders import identity
from wealthlab.portfolio.household_book import sweep, sync
from wealthlab.portfolio.orders import Trade
from wealthlab.portfolio.selection import candidates
from wealthlab.tax.funding import solve
from wealthlab.tax.funding_tax import due

ZERO = Decimal(0)
UNIT = Decimal(".000001")


class Funding:
    def __init__(self, fallback, lots):
        self.fallback = fallback
        self.lots = lots

    @property
    def basis(self):
        return self.fallback.basis

    def fund(self, ledger, wallet, spending, amounts, start, end):
        total = ZERO
        for index, source in enumerate(self.lots.plan.funding_sources):
            total += fund_source(
                self.lots, source, index, ledger, wallet, spending, amounts, start, end
            )
        return total + self.fallback.fund(ledger, wallet, spending, amounts, start, end)


def fund_source(lots, source, index, ledger, wallet, spending, amounts, start, end):
    template = order(lots, source, index, Decimal(1), lots.book)
    available = sum((lot.quantity for lot in candidates(lots.book.lots, template)), ZERO)
    maximum = max(ZERO, money(available * template.price) - source.commission)
    if not maximum:
        return ZERO

    def tax(sold):
        if not sold:
            return due(ledger.case, ledger, amounts, start, end)
        trial = deepcopy(lots.book)
        trade = sale(lots, source, index, sold, available, trial)
        trial.trade(trade)
        case, _ = recognition.apply(ledger.case, lots.case, trial, lots.when, lots.reported)
        return due(case, ledger, amounts, start, end)

    result = solve(wallet.cash, spending, maximum, tax)
    if not result["converged"]:
        raise ValueError("Lot-sale tax funding did not converge; no borrowing is assumed.")
    if not result["withdrawal"]:
        return ZERO
    trade = sale(lots, source, index, result["withdrawal"], available, lots.book)
    lots.book.trade(trade)
    ledger.case, current = recognition.apply(
        ledger.case, lots.case, lots.book, lots.when, lots.reported
    )
    lots.reported[lots.when.year] = current
    paid = sweep(lots.book, wallet)
    sync(lots.book, wallet, lots.prices)
    lots.monthly["lot_cash_swept"] += paid
    lots.monthly["lot_funding_proceeds"] += paid
    lots.funding_orders.append(trade.model_dump(mode="json"))
    lots.counter += 1
    return paid


def sale(lots, source, index, requested, available, book):
    price = lots.prices[source.security_id]
    quantity = min(
        available, ((requested + source.commission) / price).quantize(UNIT, rounding=ROUND_UP)
    )
    return order(lots, source, index, quantity, book, reserve=True)


def order(lots, source, index, quantity, book, reserve=False):
    prefix = f"household_funding_{lots.when.isoformat().replace('-', '_')}_{index}"
    suffix = str(lots.counter)
    trade_id = identity(book, prefix, suffix) if reserve else prefix + "_" + suffix
    return Trade(
        id=trade_id,
        provenance="assumption",
        date=lots.when,
        action="sell",
        account_id=source.account_id,
        security_id=source.security_id,
        quantity=quantity,
        price=lots.prices[source.security_id],
        commission=source.commission,
        selection=source.selection,
    )
