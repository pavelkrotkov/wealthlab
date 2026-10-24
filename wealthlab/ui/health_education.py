"""The HSA cash workbench precedes education and household spending integration."""

import json

import streamlit as st

from wealthlab.retirement.hsa import run
from wealthlab.retirement.hsa_example import synthetic
from wealthlab.retirement.hsa_inputs import HSACase
from wealthlab.ui.uploads import invalid, source


def show():
    st.header("Health savings account cash flows")
    st.caption(
        "Cash-only HSAs: published 2025/2026 or explicit frozen-2026 forward assumptions. "
        "Monthly eligibility is an explicit forecast; "
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
    raw = source(uploaded, synthetic().model_dump_json(indent=2), "hsa")
    if raw is None:
        return
    with st.form("hsa_case"):
        edited = st.text_area(
            "HSA coverage, funding and receipts (JSON)", key="hsa_editor", height=400
        )
        submitted = st.form_submit_button("Project HSA cash flows", type="primary")
    if submitted:
        try:
            case = HSACase.model_validate_json(edited or "")
            st.session_state["hsa_result"] = run(case)
            st.session_state["hsa_input"] = case.model_dump_json(indent=2)
        except ValueError as error:
            invalid(error, "hsa")
    result = st.session_state.get("hsa_result")
    if result is not None:
        display(result)


def display(result):
    """Separate ordinary taxable distributions from their additional tax.

    A qualified-only request can remain partly unfilled; allowing nonqualified
    cash can produce tax even when the account has sufficient assets.
    """
    st.caption(
        f"Contribution rule base: {result['rule_base_year']} · {result['rule_mode']}. "
        "Calendar-year ages and coverage still apply."
    )
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
