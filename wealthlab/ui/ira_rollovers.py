"""Show incoming direct transfers independently of outside cash and deductible deposits."""

import streamlit as st


def display(result):
    rows = result.get("incoming_rollovers", [])
    if not rows:
        return
    st.subheader("Incoming direct plan rollovers")
    st.metric(
        "Direct rollover value received inside IRAs", f"${result['incoming_rollover_value']:,.2f}"
    )
    st.caption(
        "The source plan is outside this annual IRA book. These are confirmed actual eligible "
        "cash receipts into same-owner traditional IRAs, excluding source RMDs and special "
        "features. They create no spending cash, ordinary contribution room usage or IRA "
        "deduction. Federal/NJ transferred basis is supplied independently; source allocation "
        "and eligibility are not inferred. Receipt dates precede same-day returns/withdrawals, "
        "while annual basis reconciliation can affect earlier distributions. Prior-December "
        "RMD values stay unchanged. Full household source debits require the later adapter."
    )
    labels = dict(
        date="Receipt date",
        source="Source plan",
        destination="IRA destination",
        amount="Received value",
        federal_basis_transferred="Federal basis transferred",
        nj_basis_transferred="NJ basis transferred",
    )
    st.dataframe(
        [{label: row[key] for key, label in labels.items()} for row in rows],
        hide_index=True,
        width="stretch",
    )
