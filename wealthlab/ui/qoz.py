"""Editable QOZ household policies expose tax-only inclusion beside actual liquidity."""

import streamlit as st

from wealthlab.household.scenario import Scenario
from wealthlab.products.qoz_compare import compare
from wealthlab.products.qoz_example import synthetic
from wealthlab.ui.qoz_results import display
from wealthlab.ui.uploads import invalid, source


def show():
    st.subheader("Opportunity-zone funds")
    st.warning(
        "Conditional QOF C-corporation illustration, not legal eligibility or sponsor terms. "
        "Federal denied / deferral-only / conditional ten-year election share the same "
        "contract economics. NJ has independent gain/basis and supplied limits; it cannot "
        "grant a federal election that this policy denies."
    )
    st.caption(
        "Calls are assumed optional, partially accepted subscriptions with no default penalty. "
        "They consume actual cash from executed stock sales. Returns are after entity tax; "
        "fees, internal financing, distributions and hurdle carry use the existing fund "
        "economic book. Preferred hurdle is only a carry threshold, never guaranteed income. "
        "Mandatory inclusion can require tax with no distribution. A full stock-interest "
        "sale recognizes tax before delayed settlement. The liquid reference uses the same "
        "asset returns, zero leverage/fees/carry and immediate settlement at the request. "
        "Only month-end calls/sales are supported. Pass-through clocks, opening QOF interests, "
        "transfers, return-of-capital distributions and 30-year exits require another profile."
    )
    uploaded = st.file_uploader("Load QOZ household JSON", type="json")
    year = st.selectbox("QOZ starter investment regime", [2027, 2026])
    if source(uploaded, synthetic(year).model_dump_json(indent=2), "qoz") is None:
        return
    with st.form("qoz"):
        edited = st.text_area(
            "QOZ household, actual source gains and contract (JSON)", key="qoz_editor", height=450
        )
        submitted = st.form_submit_button("Compare QOZ tax and liquidity", type="primary")
    if submitted:
        calculate(edited)
    if "qoz_result" in st.session_state:
        display(st.session_state["qoz_result"])


def calculate(edited):
    try:
        scenario = Scenario.model_validate_json(edited)
        result = compare(scenario)
        st.session_state.update(qoz_result=result, qoz_input=edited)
    except (ValueError, KeyError, TypeError) as error:
        invalid(error, "qoz")
