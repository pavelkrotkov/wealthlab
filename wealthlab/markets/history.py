"""Replay only complete observations explicitly available at the decision date.

A month is usable only after its final day. Retrieval must precede projection
start and follow the declared availability cutoff. Source/retrieval metadata
are supplied provenance, not certification of a vendor's point-in-time vintage.
One observed month maps to one projection month without interpolation, cycling,
or selection of a favorable subwindow after observing a household policy.
"""

from wealthlab.household.calendar import months


def validate_history(case, count, ids):
    history = case.historical
    if history is None:
        raise ValueError("Supply historical provenance and monthly observations.")
    if len(history.months) != count:
        raise ValueError("Historical coverage must match the projection horizon exactly.")
    dates = [r.date for r in history.months]
    validate_history_dates(dates)
    if following(dates[-1]) > history.available_as_of or history.available_as_of > case.start:
        raise ValueError("Historical observations must be complete and available by start.")
    if not history.available_as_of <= history.retrieved_on <= case.start:
        raise ValueError(
            "Historical retrieval must follow availability and precede projection start."
        )
    for row in history.months:
        validate_observation(row, ids, case.return_convention)


def following(day):
    from datetime import date

    return date(day.year + day.month // 12, day.month % 12 + 1, 1)


def validate_observation(row, ids, convention):
    if set(row.mark_returns) != ids or set(row.cash_yields) != ids:
        raise ValueError("Every historical month needs all asset marks and cash yields.")
    if convention == "total_return_reinvested" and any(row.cash_yields.values()):
        raise ValueError("Historical reinvested total returns cannot also pay cash yield.")


def validate_history_dates(dates):
    expected = [a for a, _ in months(dates[0], following(dates[-1]))]
    if any(d.day != 1 for d in dates) or dates != expected:
        raise ValueError("Historical months must be consecutive, ordered and start on day one.")
