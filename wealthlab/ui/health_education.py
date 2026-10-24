"""The HSA cash workbench precedes education and household spending integration."""

import json

import streamlit as st

from wealthlab.household.storage import MAX_BYTES
from wealthlab.retirement.hsa import run
from wealthlab.retirement.hsa_example import synthetic
from wealthlab.retirement.hsa_inputs import HSACase


def show():
    st.header("Health savings account cash flows")
    st.caption(
        "Synthetic 2025/2026 cash-only HSAs. Monthly eligibility is an explicit forecast; "
        "one row for each owner and month. Married family coverage shares one base limit "
        "when both spouses are eligible; catch-up contributions stay with each owner. "
        "No last-month-rule or testing-period benefit is assumed."
    )
    st.info(
        "Receipts represent already-paid expenses, with those payments reflected outside "
        "this workbench. Confirm qualified medical status and family eligibility. "
        "Previously reimbursed or federally deducted amounts cannot fund another tax-free "
        "withdrawal. Receipts are shared across configured HSAs and used only once."
    )
    st.caption(
        "Contributions are planning requests, not records of existing excess deposits. "
        "Direct employer funding is external; personal contributions use available cash. "
        "Salary reduction, investments, rollovers, death and excess-correction rules, "
        "education accounts and household expense funding remain unfinished. "
        "NJ treatment defaults to unconfirmed; its explicit cash-interest mode is a conditional "
        "assumption. Tax ingredients below are not a calculated annual tax saving."
    )
    uploaded = st.file_uploader("Load HSA case JSON", type="json")
    raw = uploaded.getvalue() if uploaded is not None else synthetic().model_dump_json(indent=2)
    if len(raw) > MAX_BYTES:
        st.error("HSA input exceeds the 2 MB limit.")
        return
    if st.session_state.get("hsa_source") != raw:
        st.session_state.pop("hsa_result", None)
        st.session_state.pop("hsa_input", None)
        st.session_state["hsa_source"] = raw
    with st.form("hsa_case"):
        edited = st.text_area("HSA coverage, funding and receipts (JSON)", raw, height=400)
        submitted = st.form_submit_button("Project HSA cash flows", type="primary")
    if submitted:
        try:
            case = HSACase.model_validate_json(edited or "")
            st.session_state["hsa_result"] = run(case)
            st.session_state["hsa_input"] = case.model_dump_json(indent=2)
        except ValueError as error:
            st.error(str(error))
    result = st.session_state.get("hsa_result")
    if result is not None:
        display(result)


def display(result):
    """Separate ordinary taxable distributions from their additional tax.

    A qualified-only request can remain partly unfilled; allowing nonqualified
    cash can produce tax even when the account has sufficient assets.
    """
    st.metric("Cash before tax payments", f"${result['cash']:,.2f}")
    st.subheader("Dated HSA allocation and withdrawals")
    st.dataframe(result["orders"], hide_index=True, width="stretch")
    st.metric("Funded personal federal deduction", f"${result['personal_federal_deduction']:,.2f}")
    with st.expander("Limits, remaining receipts and independent NJ assumptions", expanded=True):
        st.json(json.dumps(result, default=str))
    st.caption(
        "Nonqualified distributions are ordinary federal income. The separate 20% additional "
        "tax ends at age 65 or supplied disability date; ordinary income does not. "
        "Tax payments and medical spending are not deducted from this cash result."
    )
    st.download_button(
        "Export HSA inputs", st.session_state["hsa_input"], "hsa-case.json", "application/json"
    )
    st.download_button(
        "Export HSA result",
        json.dumps(result, default=str, indent=2),
        "hsa-result.json",
        "application/json",
    )
