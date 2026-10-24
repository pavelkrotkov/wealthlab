"""Original-year corrections remain distinct from historical payments and cash receipts."""

import streamlit as st


def display(rows, audit):
    revisions = audit.get("return_reconciliations", [])
    if not revisions:
        return
    st.subheader("January wash and original-year return reconciliation")
    records = [
        {
            "Tax year": r["year"],
            "Observed or assumed": r["observed"],
            "Liability change": r["final_result"]["total_liability"]
            - r["old_result"]["total_liability"],
            "Remaining tax": sum(r["new_owed"].values()),
            "Refund receivable at revision": sum(r["new_receivable"].values()),
            "IRA election": "Checked fixed election"
            if r["ira_eligibility"]
            else "Not applicable / not checked",
        }
        for r in revisions
    ]
    st.dataframe(records, hide_index=True, width="stretch")
    st.caption(
        "December figures were provisional while the forward wash window was unresolved. "
        "January updates the original tax year and its capital carry, then checks fixed funded "
        "IRA elections and updates future lookbacks. Historical payments stay unchanged; a "
        "tax receivable becomes cash only on its modeled refund date."
    )
    if rows[-1].get("terminal_wash_assumption"):
        st.info(
            "Final return assumes no substantially identical purchases for 30 days after "
            "the horizon. Estimated terminal tax positions include that assumption; "
            "future refunds are not deposited into horizon spending cash."
        )
