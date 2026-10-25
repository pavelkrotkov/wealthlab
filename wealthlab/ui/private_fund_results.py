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


def display_household(rows):
    st.subheader("Conditional private-fund household cash and settlement")
    audit = [r for r in rows[-1].get("sleeve_audit", []) if "fund_internal_equity" in r]
    last = audit[-1]
    a, b, c = st.columns(3)
    a.metric("Actual product cash received", f"${sum(r['sleeve_redemptions'] for r in rows):,.2f}")
    b.metric("Unsettled fund receivable", f"${last['fund_receivable']:,.2f}")
    c.metric("Complete cash liquidation", "Yes" if last["fund_complete_liquidation"] else "No")
    st.caption(
        "Investor limited liability and no calls are supplied contract assumptions. Internal "
        "fund debt remains inside NAV; settlement claims stay in wealth but cannot fund spending. "
        "Conditional allocations and actual distribution/exit taxes enter the household return "
        "without another cash receipt. Outside basis uses a separate supplied adjustment schedule."
    )
    st.json(audit)


def route_household(rows):
    from wealthlab.ui.household_sleeves import display as sleeve_results

    if any("fund_internal_equity" in r for r in rows[-1].get("sleeve_audit", [])):
        display_household(rows)
    else:
        sleeve_results(rows)
