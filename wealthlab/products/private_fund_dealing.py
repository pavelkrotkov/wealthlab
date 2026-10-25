"""Contract windows/gates reserve actual NAV; settlement receivables cannot pay bills.

Requests persist through later eligible windows. A gate limits net distributable
NAV in each window; actual transaction costs still reduce the underlying book.
A full exit is complete only when the full interest is reserved and settled.
"""

from datetime import timedelta

from wealthlab.household.calendar import money
from wealthlab.products.long_short_book import ZERO, equity, gross
from wealthlab.products.long_short_trading import redeem


def eligible(contract, when):
    period = dict(monthly=1, quarterly=3, annually=12)[contract.dealing]
    return when >= contract.lock_until and when.month % period == 0 and contract.gate_fraction > 0


def request_status(state, when):
    due = [r for r in state.contract.requests if notice_due(state.contract, r, when)]
    complete = any(r.complete_liquidation for r in due)
    requested = sum((r.amount for r in due), ZERO)
    value = max(ZERO, equity(state.book))
    outstanding = max(ZERO, requested - state.reserved)
    return complete, value, value if complete else outstanding


def notice_due(contract, request, when):
    return request.notice_date + timedelta(days=contract.notice_days) <= when


def deal(state, when, locked):
    complete, value, requested = request_status(state, when)
    result = dict(
        redemption_requested=requested,
        redemption_paid=ZERO,
        redemption_unfilled=requested,
        fund_final_reserved=False,
    )
    if locked or state.final_reserved or not eligible(state.contract, when):
        return result
    net = max(ZERO, value - money(gross(state.book) * state.case.exit_cost))
    amount = min(net if complete else requested, money(net * state.contract.gate_fraction))
    if not amount and not (complete and value == 0):
        return result
    return reserve(state, when, complete, value, amount, result)


def reserve(state, when, complete, value, amount, result):
    cash = redeem(state.book, amount, state.case.exit_cost) if value else dict(redemption_paid=ZERO)
    paid = cash.pop("redemption_paid")
    state.book["outside"] = ZERO
    state.reserved += paid
    final = complete and equity(state.book) <= 0
    state.final_reserved = final
    state.settlements.append(
        dict(
            due=when + timedelta(days=state.contract.settlement_days),
            cash=paid,
            final=final,
        )
    )
    return dict(
        result,
        **cash,
        fund_reserved_cash=paid,
        fund_final_reserved=final,
        redemption_unfilled=(
            max(ZERO, equity(state.book))
            if complete
            else max(ZERO, result["redemption_requested"] - paid)
        ),
    )


def settle(state, wallet, when):
    due = [s for s in state.settlements if s["due"] <= when]
    state.settlements = [s for s in state.settlements if s["due"] > when]
    cash = sum((s["cash"] for s in due), ZERO)
    final = any(s["final"] for s in due)
    events = state.tax.distribute(cash, final, when) if due else []
    wallet.deposit(cash)
    return cash, events
