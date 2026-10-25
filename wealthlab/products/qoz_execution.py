"""Dated dividends, stock-interest sale and settlement share one household wallet.

Distributions precede that date's ex-dividend FMV measurement. A sale applies
its contractual carry before the original-gain inclusion test; settlement
receivables remain non-interest-bearing account wealth until paid.
"""

from wealthlab.products import qoz_economics as economics
from wealthlab.products import qoz_tax
from wealthlab.products.long_short_book import ZERO, equity
from wealthlab.products.qoz_exit import exit_event


def execute(state, tranche, observation, wallet, row):
    when, events = observation.date, []
    if not tranche["sold"]:
        dividend = economics.distribute(tranche, observation)
        wallet.deposit(dividend)
        row["dividends"] += dividend
        events.append(qoz_tax.event(when, "Supplied ordinary QOF dividend", dividend=dividend))
        sale = sale_due(state, observation)
        nav = max(ZERO, equity(tranche["book"]))
        if sale:
            result = economics.sell(tranche, state.plan, when)
            nav = result["fmv"]
            tranche["economic_log"].append(dict(date=when.isoformat(), sale=result))
        included = qoz_tax.include(tranche["tax"], nav, when, state.plan, sale)
        row["original_gain_included"] += included.federal.long_term + included.federal.short_term
        events.append(included)
        if sale:
            events.append(exit_event(tranche["tax"], nav, result["proceeds"], when, state.plan))
    if tranche["settlement"] is not None and tranche["settlement"] <= when:
        wallet.deposit(tranche["receivable"])
        row["settlement_cash"] += tranche["receivable"]
        tranche["receivable"], tranche["settlement"] = ZERO, None
    return events


def sale_due(state, observation):
    return (
        observation.date >= state.plan.sale_requested
        and not observation.locked
        and (
            state.plan.mode == "liquid_reference" or observation.date >= state.plan.sale_not_before
        )
    )
