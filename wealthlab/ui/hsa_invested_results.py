"""Show actual invested-HSA assets separately from recipient cash and tax events."""

import streamlit as st


def display(rows):
    audit = rows[-1]["hsa_audit"].get("investments")
    if audit is None:
        return
    st.subheader("Invested HSA — conditional NJ securities treatment")
    a, b, c = st.columns(3)
    a.metric("Invested HSA net assets", f"${audit['net_wealth']:,.2f}")
    b.metric("Inside-HSA available cash", f"${sum(audit['cash_by_account'].values()):,.2f}")
    c.metric("HSA custodian fees owed", f"${audit['fee_summary']['cash_owed']:,.2f}")
    st.caption(
        "Marked positions and unpaid dividends count as assets, not withdrawal cash. "
        "Eligible orders can sell permitted liquid shares at observed prices; commissions "
        "and custodian fees consume assets. NJ ingredients use separately supplied basis "
        "under an explicit taxable-securities assumption; federal investment income stays "
        "inside the HSA. Recipient distribution taxes remain separately reported."
    )
    st.dataframe(audit["nj_income_by_year"], width="stretch")
