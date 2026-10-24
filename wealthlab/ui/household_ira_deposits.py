"""Funded IRA requests are separate from essential spending failures and tax cash."""

import json

import streamlit as st


def display(rows):
    if "ira_contributions" not in rows[-1]:
        return
    st.subheader("Household IRA deposits and completed eligibility")
    paid, unfilled = st.columns(2)
    paid.metric(
        "Household IRA deposits funded", f"${sum(r['ira_contributions'] for r in rows):,.2f}"
    )
    unfilled.metric(
        "Unfilled IRA deposit requests",
        f"${sum(r['ira_contributions_unfilled'] for r in rows):,.2f}",
    )
    st.caption(
        "Optional deposits use available cash after receipts and prior-tax arrears, before "
        "current tax and spending. They settle at month end after IRA withdrawals/returns. "
        "Unfilled requests do not add basis or become spending failures. Annual deductions, "
        "basis and eligibility reconcile in December after final tax-funding gains; in-year "
        "figures omit unfinalized IRA tax. No later cash backfills an earlier failed request."
    )
    with st.expander("Actual IRA deposit cash, settlement dates and eligibility checks"):
        st.dataframe(rows[-1]["ira_contribution_audit"], hide_index=True, width="stretch")
        st.json(
            json.dumps(
                [
                    r["ira_contribution_eligibility"]
                    for r in rows
                    if "ira_contribution_eligibility" in r
                ],
                default=str,
            )
        )
