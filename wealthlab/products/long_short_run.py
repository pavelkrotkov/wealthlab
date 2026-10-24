"""Paired monthly economic runs share realized paths; taxes and household budgets are separate.

Returns, charges and maintenance use observed values, then dated redemptions
and optional rebalancing occur. Final unwind respects liquidity and leaves any
full-recourse debt visible. No simulated tax-loss allocation is generated.
"""

from datetime import timedelta
from decimal import Decimal

from wealthlab.household.calendar import money
from wealthlab.products.long_short_book import ZERO, equity, gross, opening, snapshot
from wealthlab.products.long_short_margin import check
from wealthlab.products.long_short_paths import periods
from wealthlab.products.long_short_reporting import any_stage, class_counts
from wealthlab.products.long_short_returns import apply
from wealthlab.products.long_short_trading import liquidate, rebalance, redeem
from wealthlab.products.long_short_validation import validate


def run(case, batch, indices=None):
    indices = list(range(len(batch.mark_returns))) if indices is None else list(indices)
    validate(case, batch, indices)
    details = [path(case, batch, index) for index in indices]
    return dict(
        case=case.model_dump(mode="json"),
        batch_id=batch.metadata["batch_id"],
        indices=indices,
        details=details,
        scope="Pre-tax monthly economics; no household spending or inferred tax allocations",
    )


def path(case, batch, index):
    book, rows, cpi = opening(case), [], Decimal(1)
    long, short = batch.assets.index(case.long_factor), batch.assets.index(case.short_factor)
    entry_cost = money(gross(book) * case.turnover_cost)
    entry = check(book, case, is_locked(book, batch.locked[0], long, short))
    for month, (_, following) in enumerate(periods(batch)):
        when = following - timedelta(days=1)
        row = dict(
            date=when.isoformat(),
            opening_equity=equity(book),
            entry_cost=entry_cost if month == 0 else ZERO,
        )
        if month == 0:
            row.update({f"entry_{k}": v for k, v in entry.items()})
        row.update(
            apply(
                book,
                case,
                batch.mark_returns[index, month, long],
                batch.mark_returns[index, month, short],
                batch.cash_yields[index, month, long],
                batch.cash_yields[index, month, short],
            )
        )
        locked = is_locked(book, batch.locked[month], long, short)
        row.update(locked=locked, **check(book, case, locked))
        row.update(orders(book, case, when, locked))
        if eligible_rebalance(case, month, book, locked):
            row.update(rebalance(book, case))
            row.update({f"post_trade_{k}": v for k, v in check(book, case, locked).items()})
        row.update(terminal(book, case, locked, month == len(batch.dates) - 1))
        cpi *= 1 + Decimal(str(batch.inflation[index, month]))
        row.update(
            snapshot(book), real_investor_wealth=money((equity(book) + book["outside"]) / cpi)
        )
        rows.append(row)
    return dict(path=index, rows=rows, summary=summarize(case, rows))


def orders(book, case, when, locked):
    requested = sum((r.amount for r in case.redemptions if r.date == when), ZERO)
    result = dict(redemption_requested=requested, redemption_paid=ZERO, exit_cost=ZERO)
    if requested and not (book["closed"] or locked):
        result.update(redeem(book, requested, case.exit_cost))
    result["redemption_unfilled"] = requested - result["redemption_paid"]
    return result


def eligible_rebalance(case, month, book, locked):
    periods = dict(none=0, monthly=1, quarterly=3, annually=12)
    period = periods[case.rebalance]
    return (
        period and (month + 1) % period == 0 and not (book["closed"] or locked) and equity(book) > 0
    )


def is_locked(book, locks, long, short):
    return bool((book["long"] and locks[long]) or (book["short"] and locks[short]))


def summarize(case, rows):
    last, counts = rows[-1], class_counts(rows)
    return dict(
        ending_investor_wealth=last["investor_wealth"],
        investment_change=last["investor_wealth"] - case.opening_equity - case.outside_cash,
        margin_failure=bool(counts["margin_unresolved"]),
        margin_trigger_months=counts["margin_triggered"],
        negative_equity_months=counts["negative_equity"],
        product_feasible=not counts["constraints_failed"],
        forced_liquidations=sum(any_stage(r, "forced_liquidation") for r in rows),
        locked_months=sum(r["locked"] for r in rows),
        unfilled_redemptions=sum((r["redemption_unfilled"] for r in rows), ZERO),
        remaining_loan=last["financing_loan"],
        terminal_exit_blocked=last.get("terminal_exit_blocked", False),
    )


def terminal(book, case, locked, final):
    if not (final and case.exit_at_horizon) or book["closed"]:
        return {}
    if locked:
        return dict(terminal_exit_blocked=True)
    return dict(terminal_exit_blocked=False, **liquidate(book, case.exit_cost))
