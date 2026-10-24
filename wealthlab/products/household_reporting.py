"""Net assets, resolved margin actions and unresolved constraints remain distinct."""

from wealthlab.products.long_short_book import ZERO
from wealthlab.products.long_short_reporting import class_counts


def summarize(rows):
    counts = class_counts(rows)
    return dict(
        **{f"sleeve_{key}": bool(value) for key, value in counts.items()},
        sleeve_liability=sum((max(ZERO, -r["equity"]) for r in rows), ZERO),
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
