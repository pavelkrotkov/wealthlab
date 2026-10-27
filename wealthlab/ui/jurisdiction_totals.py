"""Household totals retain assessment currency and distinct actual bank cash."""

import streamlit as st

NAMES = {"PR": "Puerto Rico", "ES": "Spain"}


def display(rows):
    totals = rows[-1].get("jurisdiction_totals")
    if not totals:
        return
    st.subheader("Household tax totals by jurisdiction")
    st.caption(
        "Assessed amounts retain their tax currency; paid, refunds and payment fees are USD "
        "at actual cash-date FX. Payment books include supplied opening payments. "
        "Credits are already reflected in liabilities; federal totals include payroll. "
        "Partial and conditional assessments keep their status. Other compliance costs remain "
        "household expenses, not recorded payment fees."
    )
    records = [
        {
            "Jurisdiction": NAMES.get(row["jurisdiction"], row["jurisdiction"]),
            "Tax currency": row["currency"],
            "Assessed": row["assessed_native"],
            "Gross paid · USD": row["paid_usd"],
            "Refunds · USD": row["refunded_usd"],
            "Payment fees · USD": row["payment_fees_usd"],
            "Net cash outflow · USD": row["net_cash_usd"],
            "Assessment status": row["assessment_status"],
        }
        for row in totals
    ]
    st.dataframe(records, hide_index=True, width="stretch")
