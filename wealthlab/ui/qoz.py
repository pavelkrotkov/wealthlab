"""Editable QOZ household policies expose tax-only inclusion beside actual liquidity."""

import streamlit as st

from wealthlab.household.scenario import Scenario
from wealthlab.products.qoz_compare import compare
from wealthlab.products.qoz_example import synthetic
from wealthlab.products.qoz_transition_example import synthetic as transition_example
from wealthlab.ui.qoz_results import display
from wealthlab.ui.uploads import invalid, source


def show():
    st.subheader("Opportunity-zone funds")
    st.warning(
        "Conditional QOF C-corporation illustration, not legal eligibility or sponsor terms. "
        "Federal denied / deferral without the ten-year election / conditional ten-year "
        "election share the same "
        "contract economics. NJ has independent gain/basis and supplied limits; it cannot "
        "grant a federal election that this policy denies. Timely exit matches the named "
        "allowed case and changes only "
        "the exit/settlement constraint while retaining fund return, leverage and cost terms."
    )
    st.caption(
        "Calls are assumed optional, partially accepted subscriptions with no default penalty. "
        "They consume actual cash from executed stock sales. Returns are after entity tax; "
        "all stock lots share the same company assets, debt and costs. New cash first cures "
        "creditor debt, then retargets exposure under the supplied NAV-pricing terms. "
        "New subscriptions explicitly share same-day dividends; other entitlement terms need "
        "another profile. Cash dividends are explicitly assumed nonqualified. "
        "Preferred hurdle is only a carry threshold, never guaranteed income. "
        "Mandatory inclusion can require tax with no distribution. A full stock-interest "
        "sale recognizes tax before delayed settlement. The liquid reference uses the same "
        "asset returns, zero leverage/fees/carry and immediate settlement at the request. "
        "Only whole months and month-end calls/sales are supported. "
        "Pass-through clocks, opening QOF interests, transfers and return-of-capital "
        "distributions need another profile. Confirmed timely next-year calls revise "
        "the original return while preserving actual paid taxes/refunds; newly known "
        "refunds arrive after observation."
    )
    uploaded = st.file_uploader("Load QOZ household JSON", type="json")
    profile = st.selectbox(
        "QOZ starter investment regime",
        ["2027 same-year", "2026 legacy", "2026 gain / 2027 investment"],
    )
    example = starter(profile)
    if source(uploaded, example.model_dump_json(indent=2), "qoz") is None:
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


def starter(profile):
    if profile == "2026 gain / 2027 investment":
        return transition_example()
    return synthetic(2026 if profile == "2026 legacy" else 2027)
