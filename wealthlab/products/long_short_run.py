"""Paired monthly economic runs share realized paths; taxes and household budgets are separate.

Returns, charges and maintenance use observed values, then dated redemptions
and optional rebalancing occur. Final unwind respects liquidity and leaves any
full-recourse debt visible. No simulated tax-loss allocation is generated.
"""

from datetime import timedelta
from decimal import Decimal

from wealthlab.household.calendar import money
from wealthlab.products.long_short_book import ZERO, opening
from wealthlab.products.long_short_paths import periods
from wealthlab.products.long_short_reporting import any_stage, class_counts
from wealthlab.products.long_short_step import advance, is_locked
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
    for month, (_, following) in enumerate(periods(batch)):
        values = dict(
            long_return=batch.mark_returns[index, month, long],
            short_return=batch.mark_returns[index, month, short],
            long_yield=batch.cash_yields[index, month, long],
            short_yield=batch.cash_yields[index, month, short],
            locked=is_locked(book, batch.locked[month], long, short),
        )
        row = advance(
            book, case, values, following - timedelta(days=1), month, month == len(batch.dates) - 1
        )
        cpi *= 1 + Decimal(str(batch.inflation[index, month]))
        row["real_investor_wealth"] = money(row["investor_wealth"] / cpi)
        rows.append(row)
    return dict(path=index, rows=rows, summary=summarize(case, rows))


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
