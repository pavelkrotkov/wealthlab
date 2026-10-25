"""Conditional taxes, actual funding and unsettled exits remain separately visible."""

import json

import pandas as pd
import streamlit as st

from wealthlab.ui.market_funding_results import display as funding


def display(result):
    st.subheader("Private-fund actual cash, tax and exit outcomes")
    funding(result["fund"])
    st.dataframe(pd.DataFrame(result["fund"]["outcomes"]), hide_index=True, width="stretch")
    st.caption("Paired changes below are private fund minus the independent unlevered reference.")
    st.dataframe(pd.DataFrame(result["differences"]), hide_index=True, width="stretch")
    st.dataframe(pd.DataFrame(result["exit_status"]), hide_index=True, width="stretch")
    st.warning(
        "An outstanding interest or settlement receivable is marked wealth, not available cash "
        "or a completed after-tax exit. Final-horizon tax positions retain household obligations. "
        "Deferred/denied losses and supplied outside-basis adjustments remain independent; "
        "applicable annual capital/category limits still run. Funding success covers this "
        "supplied horizon, not lifetime retirement safety."
    )
    index = st.selectbox("Private-fund household path", result["fund"]["indices"])
    detail = next(d for d in result["fund"]["details"] if d["path"] == index)
    st.dataframe(pd.DataFrame(detail["rows"]), hide_index=True, width="stretch")
    with st.expander("Fund exposure, costs, settlement and independent basis/exit audit"):
        st.json(detail["rows"][-1]["sleeve_audit"])
    with st.expander("Reference and complete matched assumptions"):
        st.json(result["reference"])
    st.download_button(
        "Export private-fund household comparison",
        json.dumps(result, default=str),
        "private-fund-household-run.json",
        "application/json",
    )
