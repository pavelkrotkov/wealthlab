"""Inspect work-test withholding, later claims/debt and own-record benefit adjustments."""

import json

import streamlit as st

from wealthlab.retirement.social_work import run
from wealthlab.retirement.social_work_case import SocialWorkCase
from wealthlab.retirement.social_work_example import synthetic
from wealthlab.ui.uploads import invalid, source


def show():
    st.header("Social Security with employment")
    st.caption(
        "Own-record US earned W-2 wages only. Reported forecasts determine initial whole-check "
        "withholding; actual wages determine closed-year charges and reduction-factor credits. "
        "Annual and monthly limits are explicitly frozen at 2026 values in future years."
    )
    st.info(
        "Payment months and recovery fractions are conditional administrative assumptions. "
        "Government receivables and overpayment debt remain separate from spendable cash. "
        "The nested claims object is the no-work counterfactual. Auxiliary/survivor work effects, "
        "special wage payments, self-employment, Medicare withholding and earnings-history PIA "
        "recomputation are outside this profile. Household/tax execution is a separate adapter."
    )
    uploaded = st.file_uploader("Load Social Security work case JSON", type="json")
    raw = source(uploaded, synthetic().model_dump_json(indent=2), "social_work")
    if raw is None:
        return
    with st.form("social_work_case"):
        edited = st.text_area(
            "Claims, monthly forecasts and actual earned wages (JSON)",
            key="social_work_editor",
            height=400,
        )
        submitted = st.form_submit_button("Project work-test cash", type="primary")
    if submitted:
        try:
            case = SocialWorkCase.model_validate_json(edited or "")
            st.session_state["social_work_result"] = run(case)
            st.session_state["social_work_input"] = case.model_dump_json(indent=2)
        except ValueError as error:
            invalid(error, "social_work")
    if "social_work_result" in st.session_state:
        display(st.session_state["social_work_result"])


def display(result):
    st.metric("Actual projected benefit cash", f"${result['total_net_cash']:,.2f}")
    st.subheader("Annual cash by recipient")
    st.dataframe(result["annual_cash"], hide_index=True, width="stretch")
    st.subheader("Closed-year work assessments")
    st.dataframe(result["annual_work_assessments"], hide_index=True, width="stretch")
    st.subheader("Monthly cash and government positions")
    st.dataframe(result["monthly_cash"], hide_index=True, width="stretch")
    st.caption(
        "A partial work deduction still credits a full reduction-factor month. Initial whole-check "
        "overholding is refunded later; unexpected excess benefits create debt. "
        "No gross tax-loss or tax-saving cash receipt is assumed. The screen shows benefit cash, "
        "not an annual tax return or a validated spending-success probability."
    )
    with st.expander("Reduction-factor adjustments, counterfactual and sources"):
        st.json(json.dumps(result, default=str))
    st.download_button(
        "Export work-test inputs",
        st.session_state["social_work_input"],
        "social-work-case.json",
        "application/json",
    )
    st.download_button(
        "Export work-test result",
        json.dumps(result, default=str, indent=2),
        "social-work-result.json",
        "application/json",
    )
