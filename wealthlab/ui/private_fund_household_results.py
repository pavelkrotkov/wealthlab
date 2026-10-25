"""Private-fund receipts/claims aggregate by account; ordinary sleeves retain their own debt view.

The final audit contains the full dated history. Settlement claims are balances,
so only each account's latest observation contributes to outstanding claims.
Actual receipts are flows and sum across all dates without ordinary-sleeve cash.
"""

import streamlit as st


def display_household(rows):
    st.subheader("Conditional private-fund household cash and settlement")
    audit = [r for r in rows[-1].get("sleeve_audit", []) if "fund_internal_equity" in r]
    latest = {r["account_id"]: r for r in audit}
    receivable = sum(r["fund_receivable"] for r in latest.values())
    complete = all(r["fund_complete_liquidation"] for r in latest.values())
    a, b, c = st.columns(3)
    a.metric("Actual product cash received", f"${sum(r['redemption_paid'] for r in audit):,.2f}")
    b.metric("Unsettled fund receivable", f"${receivable:,.2f}")
    c.metric("Complete cash liquidation", "Yes" if complete else "No")
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
    if any("fund_internal_equity" not in r for r in rows[-1].get("sleeve_audit", [])):
        sleeve_results(rows)
