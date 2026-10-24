"""Mark-only indices and separate cash-yield diagnostics are not household forecasts.

There are no withdrawals, fees, tax payments or reinvestment decisions here.
A mark index follows one initial asset unit; cash yields accumulate separately
without interest. A declared total-return index already includes reinvestment.
The same immutable realized batch can later evaluate multiple actual policies.
"""

import numpy as np


def summarize(batch):
    index = 100 * np.cumprod(1 + batch.mark_returns, axis=1)
    opening = np.concatenate((np.full_like(index[:, :1, :], 100), index[:, :-1, :]), axis=1)
    cash = np.cumsum(opening * batch.cash_yields, axis=1)
    peaks = np.maximum.accumulate(np.concatenate((opening[:, :1, :], index), axis=1), axis=1)
    drawdown = index / peaks[:, 1:, :] - 1
    cpi = np.cumprod(1 + batch.inflation, axis=1)
    if not all(np.isfinite(a).all() for a in (index, cash, cpi)) or np.any(cpi == 0):
        raise ValueError("Market diagnostic overflow; reduce horizon or extreme assumptions.")
    return dict(
        mark_indices=index,
        separate_cash_yields=cash,
        real_buy_hold=(index + cash) / cpi[:, :, None],
        maximum_mark_drawdown=-drawdown.min(axis=1),
        inflation_index=100 * cpi,
    )


def terminal_table(batch, report):
    return [
        dict(
            asset=identity,
            mark_p05=float(np.quantile(report["mark_indices"][:, -1, i], 0.05)),
            mark_p50=float(np.quantile(report["mark_indices"][:, -1, i], 0.50)),
            mark_p95=float(np.quantile(report["mark_indices"][:, -1, i], 0.95)),
            separate_cash_p50=float(np.median(report["separate_cash_yields"][:, -1, i])),
            real_value_p50=float(np.median(report["real_buy_hold"][:, -1, i])),
            worst_mark_drawdown=float(report["maximum_mark_drawdown"][:, i].max()),
            locked_months=int(batch.locked[:, i].sum()),
        )
        for i, identity in enumerate(batch.assets)
    ]
