"""Show the selected path's conditional work changes, separate from supplied tax allocations."""

import pandas as pd
import streamlit as st


def display(result, index):
    if not result["binding"].get("employers"):
        return
    st.caption(
        "Employer factors apply net month-end marks with no separate yield or inferred tax "
        "allocation. Market locks block outgoing cash elections and retain value. The optional "
        "drawdown rule uses observed prices, starts job loss/forfeiture next month, and replaces "
        "confirmed future work changes. It is a conditional scenario rule with no calibrated "
        "event probability. Supplied vesting, rights and taxable allocations still apply."
    )
    detail = next(d for d in result["details"] if d["path"] == index)
    with st.expander("Market-linked employment changes"):
        events = [
            {
                "Worker": path["owner"],
                "Effective date": event["date"],
                "Work state": event["kind"].replace("_", " "),
                "Baseline pay multiplier": float(event["multiplier"]),
            }
            for path in detail["employment_changes"]
            for event in path["changes"]
        ]
        st.dataframe(pd.DataFrame(events), hide_index=True, width="stretch")
