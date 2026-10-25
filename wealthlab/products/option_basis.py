"""Premiums affect share tax basis/proceeds without entering economic cash twice."""

from wealthlab.household.calendar import money
from wealthlab.products.option_math import direction, units


def adjust_basis(state, leg, buy, trade_id, first):
    adjust = direction(leg) * units(leg) * leg.premium + leg.opening_fee
    if buy:
        lot = state.book.lots[trade_id]
        updated = dict(federal_basis=lot.federal_basis + adjust, nj_basis=lot.nj_basis + adjust)
        if min(updated.values()) < 0:
            raise ValueError("Negative exercise basis requires a separate special-rule adapter.")
        state.book.lots[lot.id] = lot.model_copy(update=updated)
    else:
        rows = state.book.disposals[first:]
        remaining = adjust
        for index, row in enumerate(rows):
            part = (
                money(adjust * row["quantity"] / units(leg)) if index < len(rows) - 1 else remaining
            )
            remaining -= part
            row["proceeds"] -= part
            row["federal_gross_gain"] -= part
            row["nj_gross_gain"] -= part
