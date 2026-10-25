"""Economic product checks are visible while full tax/household integrations remain open."""

import json
from importlib import import_module

import streamlit as st

from wealthlab.markets.inputs import MarketCase
from wealthlab.markets.paths import generate
from wealthlab.markets.stresses import NAMES
from wealthlab.products.long_short_compare import compare
from wealthlab.products.long_short_example import synthetic
from wealthlab.products.long_short_inputs import LongShortCase
from wealthlab.ui.long_short_results import display
from wealthlab.ui.uploads import invalid, source


def show():
    st.header("Investment products")
    workbenches = {
        "Long/short economics": None,
        "Conditional private fund": "private_funds",
        "Traditional exchange funds": "exchange_fund",
        "Whole-life illustrations": "life_illustrations",
        "Options overlays": "option_products",
    }
    workbench = st.selectbox("Product workbench", workbenches, key="products_workbench")
    module = workbenches[workbench]
    if module is not None:
        import_module(f"wealthlab.ui.{module}").show()
        return
    long_short()


def long_short():
    st.subheader("Long/short economics and margin risk")
    st.warning(
        "Pre-tax economic model. This page does not yet calculate fund tax allocations or "
        "household spending safety. Select Conditional private fund for actual household cash/tax. "
        "Supplied broker rules are assumptions, without inferred provider performance."
    )
    st.caption(
        "Long purchases use capital and then loans. Short proceeds stay segregated, cannot "
        "finance longs and earn no interest. Fees use opening notionals; month-end marks precede "
        "margin calls, redemptions and rebalancing. Full-recourse debt survives liquidation. "
        "Cash yield is not inferred to be tax-free or deductible. Outside cash is a separate "
        "zero-return reserve; it can fund configured calls and receives distributions."
    )
    mode = st.selectbox(
        "Product market mode", ["deterministic", "monte_carlo", "historical", "stress"]
    )
    stress = st.selectbox(
        "Product named stress", [*NAMES, "short_squeeze"], disabled=mode != "stress"
    )
    uploaded = st.file_uploader("Load product economic case JSON", type="json")
    if source(uploaded, json.dumps(synthetic(mode, stress), indent=2), "long_short") is None:
        return
    with st.form("long_short"):
        edited = st.text_area(
            "Market, sleeve and unlevered reference (JSON)", key="long_short_editor", height=400
        )
        submitted = st.form_submit_button("Compare long/short economics", type="primary")
    if submitted:
        calculate(edited)
    if "long_short_result" in st.session_state:
        display(st.session_state["long_short_result"])


def calculate(edited):
    try:
        data = json.loads(edited)
        market = MarketCase.model_validate(data["market"])
        sleeve = LongShortCase.model_validate(data["sleeve"])
        reference = LongShortCase.model_validate(data["reference"])
        st.session_state.update(
            long_short_result=compare(sleeve, reference, generate(market)),
            long_short_input=edited,
        )
    except (ValueError, KeyError, TypeError) as error:
        invalid(error, "long_short")
