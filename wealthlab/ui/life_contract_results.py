"""Actual cash and contingent tax stay visibly separate in policy exports."""

import json

import pandas as pd
import streamlit as st


def display(result):
    st.subheader("Executed policy cash, debt and recognition")
    st.metric("Net external policy cash", f"${result['external_cash']:,.2f}")
    st.metric("Outstanding policy debt", f"${result['closing_loan']:,.2f}")
    st.caption(
        "Tax changes below are annual liabilities, not executed cash payments or receipts. "
        "Each annual baseline is independent; no automatic multi-year carryforward or "
        "household spending-safety conclusion is made on this page. Living value and death "
        "protection are alternative outcomes. Closed policy assets are zero."
    )
    st.dataframe(pd.DataFrame(result["rows"]), hide_index=True)
    st.dataframe(pd.DataFrame(result["values"]), hide_index=True)
    annual = [
        {key: row[key] for key in ("year", "status", "unknown_fields", "tax_change")}
        for row in result["annual"]
    ]
    st.dataframe(pd.DataFrame(annual), hide_index=True)
    with st.expander("Policy source, premiums after retirement and full tax audit"):
        st.json(result)
    st.download_button(
        "Export policy contract inputs",
        json.dumps(result["inputs"], indent=2),
        "life-contract-inputs.json",
        "application/json",
    )
    st.download_button(
        "Export policy contract audit",
        json.dumps(result, default=str),
        "life-contract-audit.json",
        "application/json",
    )
    st.download_button(
        "Export policy event ledger",
        pd.DataFrame(result["rows"]).to_csv(index=False),
        "life-contract-ledger.csv",
        "text/csv",
    )
