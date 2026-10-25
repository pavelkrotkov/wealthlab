"""Underlying monthly factors cannot manufacture missing distributions or settlement quotes."""

import numpy as np


def validate_returns(batch, factors):
    if batch.metadata["input"]["return_convention"] != "price_plus_cash":
        raise ValueError(
            "Option factors need price-only returns; reinvested totals are unsupported."
        )
    columns = [batch.assets.index(factor) for factor in factors]
    if np.any(batch.cash_yields[:, :, columns]):
        raise ValueError(
            "Option factors need zero generated cash yield; supply dividends explicitly."
        )
    if np.any(batch.locked[:, columns]):
        raise ValueError("Option factor liquidity locks require a settlement-resolution adapter.")
    values = batch.mark_returns[:, :, columns]
    if not np.isfinite(values).all() or np.any(values <= -1):
        raise ValueError("Option factor returns must be finite and above complete write-off.")
