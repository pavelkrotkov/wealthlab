"""Edit matched commodity/reference price paths with explicit fixed-fact validity."""

import json

import streamlit as st

from wealthlab.products.drilling_market import DrillingMarketCase, compare
from wealthlab.products.drilling_market_example import synthetic
from wealthlab.ui.uploads import invalid, source


def show(mode, profile):
    st.caption(
        "One realized price batch drives commodity receipts and independent liquid-share prices. "
        "Production, costs, tax facts and property/exit quotes remain supplied, with explicit "
        "validity for these price paths. They are not automatically recalculated or appraised. "
        "Reference locks preserve existing restrictions; commodity-sales locks and factor "
        "cash yields require other adapters. Well issuer concentration remains unmeasured."
    )
    namespace = "drilling_market_" + mode
    uploaded = st.file_uploader("Load drilling market comparison JSON", type="json")
    starter = synthetic(mode, profile).model_dump_json(indent=2)
    if source(uploaded, starter, namespace) is None:
        return
    with st.form(namespace):
        edited = st.text_area(
            "Drilling household, price factors and validity assumptions (JSON)",
            key=namespace + "_editor",
            height=450,
        )
        submitted = st.form_submit_button("Compare drilling on shared price paths", type="primary")
    if submitted:
        calculate(edited, namespace)
    if namespace + "_result" in st.session_state:
        display(st.session_state[namespace + "_result"])


def calculate(edited, namespace):
    try:
        result = compare(DrillingMarketCase.model_validate_json(edited))
        st.session_state.update({namespace + "_result": result, namespace + "_input": edited})
    except (ValueError, KeyError, TypeError) as error:
        invalid(error, namespace)


def display(result):
    st.dataframe(
        [dict(policy=name, **o) for name, p in result["policies"].items() for o in p["outcomes"]]
    )
    st.caption(result["scope"])
    with st.expander("Matched inputs, realized price batch and actual cash/basis/tax audits"):
        st.json(json.loads(json.dumps(result, default=str)))
    st.download_button(
        "Export drilling market inputs",
        json.dumps(result["inputs"], indent=2),
        "drilling-market-inputs.json",
        "application/json",
    )
    st.download_button(
        "Export drilling market audit",
        json.dumps(result, default=str),
        "drilling-market-audit.json",
        "application/json",
    )
