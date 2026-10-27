"""Observe actual investor exits without treating zero NAV as closed gross positions.

Margin accounts remain liable for their own financing debt. A confirmed
limited-liability fund instead closes the investor interest through its actual
final settlement; internal fund leverage is not a new household obligation.
Both profiles retain tax recognition scheduled beyond the projection horizon.
"""

from wealthlab.products.long_short_book import snapshot


def record(ledger, rows):
    latest = {row["account_id"]: row for row in ledger.log}
    for sleeve in ledger.plan.sleeves:
        identity = sleeve.account_id
        pending = [event for event in ledger.allocations[identity] if event.date >= ledger.end]
        if identity in ledger.funds:
            state = fund_state(ledger.funds[identity])
            pending.extend(ledger.funds[identity].tax.deferred)
        else:
            state = dict(kind="margin_account", **snapshot(ledger.books[identity]))
        state["unrecognized_future_events"] = [e.model_dump(mode="json") for e in pending]
        latest[identity]["exit_state"] = state
    rows[-1]["sleeve_audit"] = ledger.log


def fund_state(fund):
    return dict(
        kind="limited_liability_fund",
        investor_interest_closed=fund.tax.closed,
        settlements=list(fund.settlements),
        outside_basis=dict(fund.tax.basis),
        internal_book=snapshot(fund.book),
        limited_liability_no_calls_assumed=fund.contract.limited_liability_no_calls_assumed_confirmed,
    )
