"""Synthetic eligibility switches preserve positive income and disclose incomplete basis scope."""

import streamlit as st

from wealthlab.products.loss_example import enable


def controls(household):
    if household.sleeve_plan is None:
        return household
    enabled = st.checkbox("Add synthetic conditional sleeve losses", key="sleeve_loss_example")
    if not enabled:
        return household
    st.caption(
        "Supplied illustration per annual allocation: USD 12,000 federal long-term loss and "
        "USD 12,000 NJ partnership-category loss, independent of realized market performance. "
        "Positive income remains recognized. Deferred loss release is assumed one year later; "
        "a date beyond the horizon remains unrecognized. These choices do not establish basis, "
        "at-risk/passive eligibility or a provider's loss generation. NJ category and federal "
        "capital-loss limits still apply in the annual return. Edit individual allocations "
        "below for capital versus already-allowed passive ordinary character."
    )
    federal = st.selectbox("Synthetic federal loss treatment", ["denied", "deferred", "allowed"])
    state = st.selectbox("Synthetic NJ loss treatment", ["denied", "deferred", "allowed"])
    return enable(household, federal, state)


def display(rows):
    if "sleeve_tax_assumptions" not in rows[-1]:
        return
    with st.expander("Supplied loss eligibility, deferral and basis scope"):
        st.json(rows[-1]["sleeve_tax_assumptions"])
