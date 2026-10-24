"""Keep IRA contribution funding, deductions and basis separate from withdrawals."""

import streamlit as st


def display(result):
    if result["contribution_eligibility"] is None:
        return
    st.subheader("Current-year IRA contributions and annual eligibility")
    funded = sum(r["funded"] for r in result["contribution_orders"])
    deduction = sum(p["federal_ira_deduction"] for p in result["contribution_owners"])
    a, b = st.columns(2)
    a.metric("IRA contributions funded", f"${funded:,.2f}")
    b.metric("Federal IRA deduction", f"${deduction:,.2f}")
    st.caption(
        "One cash book funds deposits and withdrawals; unfunded requests do not add basis. "
        "Current regular Roth deposits enter annual ordering, while cash cannot arrive early. "
        "The tax comparison holds funded contributions and their deduction fixed on both sides; "
        "it is not a re-optimized strategy comparison. Taxes are not paid from this workbench."
    )
    st.json(result["contribution_eligibility"])
    st.dataframe(result["contribution_orders"], hide_index=True, width="stretch")
    with st.expander("Current-year IRA deductions and separate basis additions"):
        st.json(result["contribution_owners"])
