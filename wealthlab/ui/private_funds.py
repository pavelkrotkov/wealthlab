"""Editable conditional contracts run through actual household cash, tax and market consumers."""

import json

import streamlit as st

from wealthlab.household.scenario import Scenario
from wealthlab.markets.household_inputs import HouseholdBinding
from wealthlab.markets.inputs import MarketCase
from wealthlab.markets.paths import generate
from wealthlab.markets.stresses import NAMES
from wealthlab.products.private_fund_compare import compare
from wealthlab.products.private_fund_example import synthetic
from wealthlab.ui.private_fund_results import display
from wealthlab.ui.uploads import invalid, source


def show():
    st.subheader("Conditional private-fund household comparison")
    st.warning(
        "Sponsor terms, investor eligibility, limited liability and tax treatment are explicit "
        "assumptions. This cash-only profile excludes hot assets, in-kind payments and investor "
        "debt-share changes. Independent supplied basis adjustments are required; loss schedules "
        "are assumptions, not generated tax alpha. No named provider is represented."
    )
    st.caption(
        "Underlying leverage, borrow, financing, turnover and fees use the existing economic "
        "book. Contract lock, notice, dealing windows, gate and settlement determine actual "
        "household cash. The reference is an independently configured unlevered cash-distribution "
        "tax proxy. Its tax profile is an assumption, not an ETF or security-lot tax model. "
        "Federal capital/passive ordinary and NJ allocation characters are independently editable; "
        "denied/deferred/allowed loss choices do not automatically alter supplied outside basis."
    )
    mode = st.selectbox(
        "Private-fund market mode", ["deterministic", "monte_carlo", "historical", "stress"]
    )
    stress = st.selectbox(
        "Private-fund stress", [*NAMES, "short_squeeze"], disabled=mode != "stress"
    )
    uploaded = st.file_uploader("Load private-fund comparison JSON", type="json")
    if source(uploaded, json.dumps(synthetic(mode, stress), indent=2), "private_fund") is None:
        return
    with st.form("private_fund"):
        edited = st.text_area(
            "Contracts, independent basis/allocations and household (JSON)",
            key="private_fund_editor",
            height=400,
        )
        submitted = st.form_submit_button("Compare conditional private fund", type="primary")
    if submitted:
        calculate(edited)
    if "private_fund_result" in st.session_state:
        display(st.session_state["private_fund_result"])


def calculate(edited):
    try:
        data = json.loads(edited)
        result = compare(
            Scenario.model_validate(data["fund"]),
            Scenario.model_validate(data["reference"]),
            generate(MarketCase.model_validate(data["market"])),
            HouseholdBinding.model_validate(data["binding"]),
        )
        st.session_state.update(private_fund_result=result, private_fund_input=edited)
    except (ValueError, KeyError, TypeError) as error:
        invalid(error, "private_fund")
