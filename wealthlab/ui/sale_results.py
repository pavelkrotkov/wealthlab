"""Keep decision outcomes readable while the export retains the complete execution record."""

import streamlit as st


def display(decisions):
    if not decisions:
        return
    st.subheader("Sale decisions · gross wealth targets")
    rows = [
        {
            "Decision": row["policy"],
            "Date": row["date"],
            "Shares sold": row["sold_units"],
            "Unfilled": row["unfilled_units"],
            "Before": percent(row["weight_before"]),
            "After": percent(row["weight_after"]),
            "Fee": row["commission"],
        }
        for row in decisions
    ]
    st.dataframe(
        rows,
        hide_index=True,
        width="stretch",
        column_config={
            "Before": st.column_config.NumberColumn(format="%.2f%%"),
            "After": st.column_config.NumberColumn(format="%.2f%%"),
            "Fee": st.column_config.NumberColumn(format="$%.2f"),
        },
    )
    st.caption("Before/after weights include every configured account and cash, before tax.")


def percent(value):
    return None if value is None else float(value * 100)
