"""Salary reductions transfer payroll assets; direct employer funding is external."""

import streamlit as st


def display(rows):
    if "hsa_payroll_contributions" not in rows[-1]:
        return
    st.subheader("HSA payroll salary reductions")
    a, b, c = st.columns(3)
    a.metric(
        "Funded HSA salary reductions", f"${sum(r['hsa_payroll_contributions'] for r in rows):,.2f}"
    )
    b.metric(
        "Unfilled HSA salary elections", f"${sum(r['hsa_payroll_unfilled'] for r in rows):,.2f}"
    )
    c.metric(
        "External employer HSA funding", f"${sum(r['hsa_employer_funding'] for r in rows):,.2f}"
    )
    st.caption(
        "Confirmed qualifying section125 salary reductions use the owner's current monthly "
        "gross wages after all funded employee401k elections, annual HSA room and actual cash. "
        "They reduce federal wages/payroll taxes without another personal deduction. "
        "Conditional NJ treatment preserves taxable salary in both liability and withholding. "
        "Employer-reported contributions include salary reductions; only direct employer "
        "funding adds external assets. First-day orders use pooled monthly payroll, not "
        "an intramonth payroll certification. Ordinary after-tax payroll deductions remain "
        "personal deposits. Partners and ineligible S-corporation owners are outside this profile."
    )
