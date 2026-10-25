"""Editable conditional contracts and matched household outcomes.

Contribution presets retain one actual source account/lot; they do not create
another cash balance or alter independently supplied contract and tax facts.
"""

import json

import streamlit as st

from wealthlab.household.scenario import Scenario
from wealthlab.markets.inputs import MarketCase
from wealthlab.markets.paths import generate
from wealthlab.products.exchange_fund_allocation_example import CHOICES, allocation_example
from wealthlab.products.exchange_fund_compare import compare
from wealthlab.products.exchange_fund_market import bind
from wealthlab.products.exchange_fund_market_example import synthetic as market_example
from wealthlab.ui.exchange_fund_results import display
from wealthlab.ui.uploads import invalid, source


def show():
    st.subheader("Traditional exchange funds")
    st.warning(
        "Conditional synthetic contract, not a sponsor quote or legal qualification. Deferred "
        "tax remains in independent bases and eventual sale gains; it is not eliminated. "
        "Unconfirmed contribution/distribution treatment blocks calculation."
    )
    st.caption(
        "Both policies use the same price-only basket benchmark. Direct sale realizes source "
        "gains and buys a liquid basket at opening, with zero assumed direct fees. Fund fees "
        "reduce NAV; supplied cash distributions and tax/basis adjustments are independent. "
        "sell_liquid sells basket shares; sell_source sells actual retained source shares. "
        "Zero contribution creates no fund and rejects fund-only cash/tax facts. "
        "Dated requests raise actual household cash; there is no automatic product sale "
        "for a bill. A locked account can coexist with spending/tax shortfalls. Partial "
        "redemptions, debt, qualification, statutory basket allocation and excess-basis cash "
        "distributions need other adapters. Edit the complete household and contract below."
    )
    uploaded = st.file_uploader("Load exchange household JSON", type="json")
    mode = st.selectbox(
        "Exchange price source", ["entered", "deterministic", "stress", "monte_carlo"]
    )
    contribution = st.selectbox("Synthetic contribution profile", CHOICES)
    scenario = allocation_example(contribution)
    data = {"scenario": scenario.model_dump(mode="json")}
    if mode != "entered":
        data.update(
            market=market_example(scenario, mode).model_dump(mode="json"),
            replace_observations_with_market_confirmed=True,
            path=0,
        )
    starter = json.dumps(data, indent=2)
    if source(uploaded, starter, "exchange_fund") is None:
        return
    with st.form("exchange_fund"):
        edited = st.text_area(
            "Exchange household and optional realized market (JSON)",
            key="exchange_fund_editor",
            height=450,
        )
        submitted = st.form_submit_button("Compare exchange fund and direct sale", type="primary")
    if submitted:
        calculate(edited)
    if "exchange_fund_result" in st.session_state:
        display(st.session_state["exchange_fund_result"])


def calculate(edited):
    try:
        data = json.loads(edited)
        scenario = Scenario.model_validate(data["scenario"])
        if "market" in data:
            if data.get("replace_observations_with_market_confirmed") is not True:
                raise ValueError("Confirm replacing price observations with the supplied market.")
            batch = generate(MarketCase.model_validate(data["market"]))
            scenario = bind(scenario, batch, data.get("path", 0))
        result = compare(scenario)
        result["submitted_input"] = data
        st.session_state.update(exchange_fund_result=result, exchange_fund_input=edited)
    except (ValueError, KeyError, TypeError) as error:
        invalid(error, "exchange_fund")
