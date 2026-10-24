"""Validate realized observation axes and admissible economic return conventions.

This profile has no terminal delisting or daily pricing adapter. Complete
write-off marks are therefore rejected before a rebalance could repurchase
an exposure whose price has become zero. The ordinary generator remains the
source of dates and joint paths, with no re-sampling per policy.
"""

import numpy as np

from wealthlab.household.calendar import months


def validate(batch):
    dates = tuple(start for start, _ in periods(batch))
    shape = (len(batch.mark_returns), len(dates), len(batch.assets))
    shapes = (
        batch.mark_returns.shape,
        batch.cash_yields.shape,
        batch.inflation.shape,
        batch.locked.shape,
    )
    if tuple(batch.dates) != dates or shapes != (shape, shape, shape[:2], shape[1:]):
        raise ValueError(
            "Long/short batch observations must cover every supplied month and factor."
        )
    if not all(
        np.isfinite(a).all() for a in (batch.mark_returns, batch.cash_yields, batch.inflation)
    ):
        raise ValueError("Long/short observations must be finite.")
    validate_rates(batch)


def validate_rates(batch):
    if (
        (batch.mark_returns <= -1).any()
        or (batch.cash_yields < 0).any()
        or (batch.inflation <= -1).any()
    ):
        raise ValueError("Nonnegative yield and marks above complete write-off are required.")


def periods(batch):
    from datetime import date

    source = batch.metadata["input"]
    return months(date.fromisoformat(source["start"]), date.fromisoformat(source["end"]))
