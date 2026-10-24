"""Contribution allocation is the first vertical layer of the retirement workbench."""

import json

import streamlit as st

from wealthlab.household.storage import MAX_BYTES
from wealthlab.retirement.contribution_example import synthetic
from wealthlab.retirement.contribution_inputs import ContributionCase
from wealthlab.retirement.contributions import run


def show():
    st.header("Retirement contributions")
    st.caption(
        "Synthetic annual allocation. Published 2025/2026 traditional/Roth IRA and employee "
        "401(k) limits only. Contributions are requests; only eligible, cash-funded amounts "
        "reach accounts. All amounts are USD."
    )
    st.info(
        "Enter full-year eligible compensation, each IRA-specific MAGI, workplace coverage "
        "and plan eligibility as explicit assumptions. Joint filers allocate IRA compensation "
        "budgets between owners; their sum cannot exceed combined eligible compensation. "
        "Unused budgets are not automatically reassigned."
    )
    st.caption(
        "Opening balances include prior-year activity only. Include all current-year "
        "contributions across IRAs and one covered employer per owner as dated orders. "
        "Multi-employer catch-up rules are unfinished. Cash receipts precede same-day "
        "orders; earlier orders have funding priority. This layer excludes employer matches, "
        "403(b)/457/SIMPLE/SEP exceptions, HSA/education, withdrawals and household tax funding; "
        "these remain unfinished retirement-ticket scope. Existing excess contributions need "
        "a separate correction model and must not be entered as funded opening history."
    )
    uploaded = st.file_uploader("Load retirement contribution JSON", type="json")
    raw = uploaded.getvalue() if uploaded is not None else synthetic().model_dump_json(indent=2)
    if len(raw) > MAX_BYTES:
        st.error("Contribution input exceeds the 2 MB limit.")
        return
    if st.session_state.get("retirement_source") != raw:
        st.session_state.pop("retirement_result", None)
        st.session_state.pop("retirement_input", None)
        st.session_state["retirement_source"] = raw
    with st.form("retirement_contributions"):
        edited = st.text_area("Contribution assumptions and dated orders (JSON)", raw, height=400)
        submitted = st.form_submit_button("Allocate contributions", type="primary")
    try:
        if submitted:
            case = ContributionCase.model_validate_json(edited or "")
            st.session_state["retirement_result"] = run(case)
            st.session_state["retirement_input"] = case.model_dump_json(indent=2)
        result = st.session_state.get("retirement_result")
        if result is not None:
            st.download_button(
                "Export contribution inputs JSON",
                st.session_state["retirement_input"],
                "contribution-case.json",
                "application/json",
            )
            display(result)
    except ValueError as error:
        st.error(str(error))


def display(result):
    st.metric("Unallocated cash", f"${result['cash']:,.2f}")
    st.subheader("Requested, eligible and funded contributions")
    st.dataframe(result["orders"], hide_index=True, width="stretch")
    st.subheader("Deductions and new basis by owner")
    st.dataframe(result["owners"], hide_index=True, width="stretch")
    st.caption(
        "IRA deduction uses actual funded contributions. NJ traditional IRA contributions "
        "are previously taxed basis; pretax 401(k) deferrals remain subject to payroll tax. "
        "Basis additions exclude opening basis and are not a complete distribution ledger. "
        "Tax liability and spending safety are not calculated on this screen yet."
    )
    with st.expander("Ending balances and rule sources"):
        st.json(dict(accounts=result["account_balances"], sources=result["sources"]))
    st.download_button(
        "Export contribution result JSON",
        json.dumps(result, default=str, indent=2),
        "contribution-result.json",
        "application/json",
    )
