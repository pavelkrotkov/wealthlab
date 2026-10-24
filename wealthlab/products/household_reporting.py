"""Separate net asset value, economic exposures and collateral-policy failures.

Required margin not posted is a policy failure, not a duplicate consumption
bill. A negative account value is a liability; optional unfilled redemption
requests do not themselves become household spending shortfalls.
"""

from wealthlab.products.long_short_book import ZERO
from wealthlab.products.long_short_run import any_stage


def summarize(rows):
    return dict(
        sleeve_liability=sum((max(ZERO, -r["equity"]) for r in rows), ZERO),
        sleeve_failure=any(failed(r) for r in rows),
        sleeve_margin_call_not_funded=sum(
            (
                r.get(f"{p}margin_unfunded", ZERO)
                for r in rows
                for p in ("entry_", "", "post_trade_")
            ),
            ZERO,
        ),
        sleeve_redemptions=sum((r["redemption_paid"] for r in rows), ZERO),
        sleeve_positions=[
            {
                k: r[k]
                for k in (
                    "account_id",
                    "long_factor",
                    "short_factor",
                    "long_value",
                    "short_liability",
                    "equity",
                    "financing_loan",
                )
            }
            for r in rows
        ],
    )


def failed(row):
    return (
        any_stage(row, "margin_unfunded")
        or row.get("terminal_exit_blocked", False)
        or row["equity"] < 0
    )
