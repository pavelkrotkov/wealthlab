"""One corporation pays dividends/sale costs and settles once; stock lots share its NAV.

A source-gain lot preserves its own election clock and basis. It never owns
an independent creditor book. Actual cash and tax-only recognition remain
separate even when a sale precedes delayed settlement.
"""

from wealthlab.products import qoz_economics as economics
from wealthlab.products import qoz_tax
from wealthlab.products.long_short_book import ZERO, equity
from wealthlab.products.qoz_dates import sale_due
from wealthlab.products.qoz_exit import exit_event
from wealthlab.products.qoz_units import allocate


def execute(state, observation, wallet, row):
    fund = state.economic
    if fund is None:
        return []
    events = []
    if not fund["sold"]:
        dividend = economics.distribute(fund, observation)
        wallet.deposit(dividend)
        row["dividends"] += dividend
        events.append(
            qoz_tax.event(observation.date, "Supplied ordinary QOF dividend", dividend=dividend)
        )
        events.extend(stock_events(state, observation, dividend, row))
    if fund["settlement"] is not None and fund["settlement"] <= observation.date:
        wallet.deposit(fund["receivable"])
        row["settlement_cash"] += fund["receivable"]
        fund["receivable"], fund["settlement"] = ZERO, None
    return events


def stock_events(state, observation, dividend, row):
    fund, when = state.economic, observation.date
    sale = sale_due(state.plan, observation)
    nav = max(ZERO, equity(fund["book"]))
    result = economics.sell(fund, state.plan, when) if sale else dict(fmv=nav, proceeds=ZERO)
    if sale:
        state.economic_log.append(dict(date=when.isoformat(), sale=result))
    navs = allocate(result["fmv"], state.tranches)
    proceeds = allocate(result["proceeds"], state.tranches)
    dividends = allocate(dividend, state.tranches)
    state.stock_values.append(
        dict(
            date=when.isoformat(),
            values={t["id"]: value for t, value in zip(state.tranches, navs, strict=True)},
        )
    )
    events = []
    for lot, value, paid, distributed in zip(
        state.tranches, navs, proceeds, dividends, strict=True
    ):
        lot["dividends"] += distributed
        included = qoz_tax.include(lot["tax"], value, when, state.plan, sale)
        row["original_gain_included"] += included.federal.long_term + included.federal.short_term
        events.append(included)
        if sale:
            events.append(exit_event(lot["tax"], value, paid, when, state.plan))
    return events
