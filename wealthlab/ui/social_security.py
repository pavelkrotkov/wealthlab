"""Compare fixed claims with source-backed month and offset rules.

The optional reference scope is explicit. A reproduced Owl difference remains
visible and never replaces the native SSA-backed entitlement or issued cash.
"""

import json

import streamlit as st

from wealthlab.retirement.social import run
from wealthlab.retirement.social_example import synthetic
from wealthlab.retirement.social_inputs import SocialCase
from wealthlab.ui.uploads import invalid, source


def show():
    st.header("Social Security ordinary claims")
    st.caption(
        "Monthly own and ordinary spouse claims for births after January 1, 1943. "
        "PIA inputs are January-2026 SSA dime amounts, "
        "not rounded benefit checks. Future COLAs are explicit assumptions, applied to "
        "December entitlement and the following January's cash. Claim dates are "
        "fixed inputs; no optimizer changes them here. Current claim rules are held fixed "
        "into future years, not represented as guaranteed future law."
    )
    st.info(
        "Confirm no earnings-test deductions, other record auxiliaries or prior adjustments, "
        "and survival of "
        "all members through this projection. Partner eligibility is supplied, not inferred "
        "from a shared household. Ordinary own/spouse claims follow the same application; "
        "a spouse add-on cannot start before the insured partner claims. Own delayed credits "
        "reduce the additional spouse amount."
    )
    st.caption(
        "Entitlement and payment months are distinct. Before age 70, credits earned in a "
        "claim year may not enter benefits until January entitlement of the next year. "
        "The following-month cash convention excludes benefit/premium/tax offsets and actual "
        "Wednesday payment dates. Survivor benefits, work-test deductions and later "
        "recomputation, special histories, earnings-to-PIA reconstruction, Medicare withholding "
        "and household annual-tax integration remain unfinished. Do not treat a confirmed "
        "no-deduction assumption as valid after changing wages."
    )
    uploaded = st.file_uploader("Load Social Security case JSON", type="json")
    raw = source(uploaded, synthetic().model_dump_json(indent=2), "social")
    if raw is None:
        return
    with st.form("social_case"):
        edited = st.text_area(
            "PIA, eligibility and fixed claim dates (JSON)", key="social_editor", height=400
        )
        submitted = st.form_submit_button("Project Social Security claims", type="primary")
    if submitted:
        try:
            case = SocialCase.model_validate_json(edited or "")
            st.session_state["social_result"] = run(case)
            st.session_state["social_input"] = case.model_dump_json(indent=2)
        except ValueError as error:
            invalid(error, "social")
    if "social_result" in st.session_state:
        display(st.session_state["social_result"])


def display(result):
    st.metric("Issued benefits before offsets", f"${result['total_issued_before_offsets']:,.2f}")
    st.subheader("Annual cash by recipient")
    st.dataframe(result["annual_cash"], hide_index=True, width="stretch")
    with st.expander("Monthly entitlement, delayed credits and additional spouse benefit"):
        st.dataframe(result["cash_months"], hide_index=True, width="stretch")
    st.caption(
        "An owner's own delayed credits do not increase their spouse's base benefit. "
        "A recipient's own delayed credits reduce their additional spouse benefit. "
        "No earnings or household tax benefit is calculated on this screen."
    )
    st.subheader("Limited Owl reference comparison")
    comparison = result["owl_comparison"]
    st.caption(comparison.get("reason", comparison.get("limitations", "")))
    st.dataframe(comparison["rows"], hide_index=True, width="stretch")
    with st.expander("FRA dates, future assumptions and sources"):
        st.json(json.dumps(result, default=str))
    st.download_button(
        "Export Social Security inputs",
        st.session_state["social_input"],
        "social-security-case.json",
        "application/json",
    )
    st.download_button(
        "Export Social Security result",
        json.dumps(result, default=str, indent=2),
        "social-security-result.json",
        "application/json",
    )
