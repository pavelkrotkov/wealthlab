"""Distinguish assessed, paid and unpaid fees from costs already embedded in prices."""

import streamlit as st


def display(result):
    if not result["fee_assessments"]:
        return
    st.subheader("Portfolio fees")
    fees = result["fee_summary"]
    st.caption(
        f"Cash fees assessed: USD {fees['cash_assessed']:,.2f}; "
        f"paid: USD {fees['cash_paid']:,.2f}; still owed: USD {fees['cash_owed']:,.2f}. "
        f"Embedded estimate: USD {fees['embedded_estimate']:,.2f} (already in supplied prices)."
    )
    st.dataframe(result["fee_assessments"], hide_index=True, width="stretch")
    st.caption(
        "Each assessment uses its own date, price snapshot, scope and day count. "
        "Unpaid cash fees reduce marked wealth once; later proceeds settle them before "
        "reinvestment. Embedded estimates are not charged again. No fee tax deduction is assumed."
    )
