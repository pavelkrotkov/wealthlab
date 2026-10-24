"""529 funding, annual qualified-expense allocation and separate tax recipients."""

import json

import streamlit as st

from wealthlab.retirement.education import run
from wealthlab.retirement.education_example import synthetic
from wealthlab.retirement.education_inputs import EducationCase
from wealthlab.ui.uploads import invalid, source


def show():
    st.header("Education account projections")
    st.caption(
        "Savings-type 529 accounts, 2025/2026 higher education only. Plan limits apply "
        "across all configured accounts for the same plan and beneficiary. Contributions "
        "use actual cash; returns are net assumed account returns. Gift-tax limits are not "
        "contribution caps. Confirm all relevant accounts and education benefits."
    )
    st.info(
        "Allocate each year's qualified expenses explicitly between accounts and recipients. "
        "Tax-free aid, expenses used for credits and expenses used by other vehicles are "
        "reserved first. Payments must occur in the selected year; a later same-year payment "
        "can qualify an earlier distribution. Confirm institution and expense eligibility, "
        "including any room/board limit. The expense ledger does not debit household cash. "
        "Reimbursed expenses must already be reflected outside this workbench; direct-institution "
        "payments leave modeled assets once."
    )
    st.caption(
        "Owner payments reimburse household cash only if the owner is a household cash member. "
        "Student and direct-institution payments are assigned to the beneficiary for tax; "
        "external payments do not enter household cash. Conditional additional-tax exceptions "
        "are supplied as taxable earnings covered, not as a scholarship's face value. "
        "NJBEST nonqualified principal recapture remains unknown unless explicitly supplied. "
        "No annual tax saving, tax payment or gift/estate conclusion is calculated here. "
        "Coverdell, K-12, credentials, loans, refunds and rollovers remain unfinished."
    )
    uploaded = st.file_uploader("Load education case JSON", type="json")
    raw = source(uploaded, synthetic().model_dump_json(indent=2), "education")
    if raw is None:
        return
    with st.form("education_case"):
        edited = st.text_area(
            "529 accounts, events and expense allocations (JSON)",
            key="education_editor",
            height=400,
        )
        submitted = st.form_submit_button("Project education accounts", type="primary")
    if submitted:
        try:
            case = EducationCase.model_validate_json(edited or "")
            result = run(case)
            st.session_state["education_result"] = result
            st.session_state["education_input"] = case.model_dump_json(indent=2)
        except ValueError as error:
            invalid(error, "education")
    if "education_result" in st.session_state:
        display(st.session_state["education_result"])


def display(result):
    st.metric("Household cash before tax payments", f"${result['cash']:,.2f}")
    st.subheader("Dated 529 funding and payments")
    st.dataframe(result["orders"], hide_index=True, width="stretch")
    st.subheader("Annual income by account and tax recipient")
    st.dataframe(result["annual_tax_groups"], hide_index=True, width="stretch")
    st.caption(
        "Distributed principal is not federal income. Only earnings allocable to unqualified "
        "amounts are taxable. Qualified expenses are never reused across accounts. NJ income "
        "is unknown where previously deducted NJBEST principal has not been reconciled. "
        "The potential NJBEST deduction uses funded contributions and supplied final NJ gross "
        "income for one return; it is not a cash refund or a complete deduction-history ledger."
    )
    with st.expander("Ending basis, deductions, expense reservations and sources", expanded=True):
        st.json(json.dumps(result, default=str))
    st.download_button(
        "Export education inputs",
        st.session_state["education_input"],
        "education-case.json",
        "application/json",
    )
    st.download_button(
        "Export education result",
        json.dumps(result, default=str, indent=2),
        "education-result.json",
        "application/json",
    )
