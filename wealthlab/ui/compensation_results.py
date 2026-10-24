"""Expose contingent value, locked value and optional cash requests without inventing liquidity."""

import pandas as pd
import streamlit as st


def display(rows):
    last = rows[-1]
    if "employer_vested" not in last:
        return
    st.subheader("Employer-linked value and liquidity")
    vested, contingent, locked = st.columns(3)
    vested.metric("Vested employer value", f"${last['employer_vested']:,.2f}")
    contingent.metric("Unvested contingent value", f"${last['employer_unvested_contingent']:,.2f}")
    locked.metric("Locked vested value", f"${last['employer_locked_vested']:,.2f}")
    not_paid = sum(r["employer_distribution_not_paid"] for r in rows)
    st.caption(
        f"Employer exposure is {last['employer_share_of_assets_plus_contingent']:.2%} "
        "of gross marked assets plus contingent value. "
        f"Unpaid optional distribution requests total ${not_paid:,.2f}; actual spending "
        "shortfalls remain in the household funding result. Tax results use supplied "
        "allocations and cash rights. Basis and hypothetical exit tax remain unmodeled."
    )
    with st.expander("Employer value path"):
        columns = ["employer_vested", "employer_unvested_contingent", "employer_locked_vested"]
        st.line_chart(pd.DataFrame(rows).set_index("date")[columns].astype(float))
