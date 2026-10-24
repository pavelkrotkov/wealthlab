"""Actual healthcare payments and unpaid liabilities remain separate from HSA transfers."""

import json

import streamlit as st


def display(rows):
    bills = rows[-1]["hsa_audit"]["medical_bills"]
    if not bills["remaining"]:
        return
    st.subheader("Current medical bills and arrears")
    a, b, c = st.columns(3)
    a.metric(
        "Direct HSA medical payments", f"${sum(r['medical_provider_paid'] for r in rows):,.2f}"
    )
    b.metric("Cash medical bill payments", f"${sum(r['medical_cash_paid'] for r in rows):,.2f}")
    c.metric("Unpaid medical bill liability", f"${rows[-1]['medical_owed']:,.2f}")
    st.caption(
        "Bills are net of insurance and excluded from other budgets and deductions. "
        "Direct HSA payments go to providers; they are not household cash receipts. "
        "Cash pays the remainder after Medicare in the healthcare slot. Unpaid bills "
        "remain liabilities; curing arrears does not increase recurring reserve demand. "
        "Only actual cash-paid, undeducted portions become later reimbursement capacity. "
        "The shared receipt book prevents reuse across owners and years. "
        "No automatic medical deduction or insurance claim is generated."
    )
    with st.expander("Medical bill payments and remaining liabilities"):
        st.json(json.dumps(bills, default=str), expanded=False)
