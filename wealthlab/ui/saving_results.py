"""Scheduled investment is optional; show actual purchases and unfilled budgets."""

import streamlit as st


def display(rows):
    if "saving_audit" not in rows[-1]:
        return
    st.subheader("Actual scheduled liquid saving")
    a, b = st.columns(2)
    a.metric("Cash invested including commissions", f"${sum(r['saving_spent'] for r in rows):,.2f}")
    b.metric("Unfilled saving budgets", f"${sum(r['saving_unfilled'] for r in rows):,.2f}")
    st.caption(
        "Saving uses received cash after reserving current modeled bills, taxes and the "
        "chosen cash buffer. Market locks and commissions constrain actual shares. "
        "New purchases share the existing basis and wash-sale history."
    )
    with st.expander("Saving budgets and actual share purchases"):
        st.json(rows[-1]["saving_audit"])
