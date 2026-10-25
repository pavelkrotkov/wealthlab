"""Observed allocations retain execution costs and unfilled targets."""

import streamlit as st


def display(audit):
    decisions = audit.get("rebalance_decisions", [])
    if not decisions:
        return
    st.subheader("Actual taxable rebalancing")
    st.caption(
        "Weights describe this account's securities, excluding cash. Targets use values before "
        "this decision's costs. Gross sales respect the sale cap; purchases use only those net "
        "receipts. Existing cash is swept normally. Locks, commissions and rounding can leave "
        "unfilled targets. Harvesting runs first; actual repurchases can defer a harvested loss. "
        "Tax payments and spending happen afterward and can change the final allocation."
    )
    st.dataframe(
        [{k: v for k, v in d.items() if k not in {"securities", "trade_ids"}} for d in decisions],
        hide_index=True,
        width="stretch",
    )
    st.dataframe(
        [
            dict(policy=d["policy"], date=d["date"], **row)
            for d in decisions
            for row in d["securities"]
        ],
        hide_index=True,
        width="stretch",
    )
