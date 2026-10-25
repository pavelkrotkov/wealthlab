"""Edit conditional drilling facts and compare actual household cash/tax outcomes."""

import json

import streamlit as st

from wealthlab.household.scenario import Scenario
from wealthlab.products.drilling_compare import compare
from wealthlab.products.drilling_example import synthetic
from wealthlab.ui.drilling_results import display
from wealthlab.ui.uploads import invalid, source


def show():
    st.subheader("Drilling partnerships")
    st.warning(
        "Conditional cash-basis synthetic contract. GP/LP labels establish neither "
        "deduction eligibility nor a guaranteed liability cap. SE/QBI/AMT facts and "
        "deduction limits are independently supplied. Ordinary NIIT exclusion also needs "
        "its own supplied classification; full-tax optimization is unsupported."
    )
    st.caption(
        "Capital calls and creditor claims use actual household cash. Unpaid creditors "
        "and recourse liabilities survive exhausted investment capital. Production quantity "
        "times commodity price funds paid costs and distributions. No headline tax-saving "
        "receipt is deposited. The liquid alternative uses actual shares, the same capital "
        "budget and explicit cash requests; its zero-fee/price-only profile is an assumption. "
        "Edit residual property values, prelimited deduction and supplemental SE/QBI/AMT "
        "facts together when changing the production path. No statutory IDC, depletion, "
        "QBI carry or AMT-credit eligibility engine is inferred."
    )
    profile = st.selectbox(
        "Drilling synthetic case",
        ["base", "poor_production", "denied", "deferred", "liability_call"],
    )
    uploaded = st.file_uploader("Load drilling household JSON", type="json")
    starter = json.dumps(synthetic(profile).model_dump(mode="json"), indent=2)
    if source(uploaded, starter, "drilling") is None:
        return
    with st.form("drilling"):
        edited = st.text_area(
            "Drilling household, cash and tax assumptions (JSON)", key="drilling_editor", height=450
        )
        submitted = st.form_submit_button("Compare drilling and liquid investment", type="primary")
    if submitted:
        calculate(edited)
    if "drilling_result" in st.session_state:
        display(st.session_state["drilling_result"])


def calculate(edited):
    try:
        scenario = Scenario.model_validate_json(edited)
        result = compare(scenario)
        st.session_state.update(drilling_result=result, drilling_input=edited)
    except (ValueError, KeyError, TypeError) as error:
        invalid(error, "drilling")
