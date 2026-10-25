"""Editable dated option contracts, complete accounting and explicit tax uncertainty."""

import json

import pandas as pd
import streamlit as st

from wealthlab.products.option_engine import run
from wealthlab.products.option_example import synthetic
from wealthlab.products.option_inputs import OptionCase
from wealthlab.products.option_stress import stress
from wealthlab.ui.uploads import invalid, source


def show():
    st.subheader("Options overlays and synthetic exposure")
    st.warning(
        "Conditional contract and broker assumptions. Model values are not historical quotes. "
        "Tax classification, straddles, covered calls, holding periods and constructive sales "
        "require explicit independent assumptions. No guaranteed aggregate floor is inferred."
    )
    strategy = st.selectbox(
        "Option example",
        ["Covered call", "Collar", "Four-leg synthetic exposure"],
        key="option_example",
    )
    uploaded = st.file_uploader("Load dated option JSON", type="json")
    if (
        source(uploaded, synthetic(strategy).model_dump_json(indent=2), f"option_{strategy}")
        is None
    ):
        return
    with st.form("option_products"):
        edited = st.text_area(
            "Option terms, marks, events and tax assumptions (JSON)",
            key=f"option_{strategy}_editor",
            height=450,
        )
        submitted = st.form_submit_button("Run dated options", type="primary")
    if submitted:
        calculate(edited)
    if "option_result" in st.session_state:
        display(st.session_state["option_result"])


def calculate(edited):
    try:
        case = OptionCase.model_validate_json(edited)
        result = run(case)
        result["stress"] = stress(case)
        st.session_state["option_result"] = result
    except (ValueError, KeyError, TypeError) as error:
        invalid(error, "option")


def display(result):
    st.subheader("Dated option cash, shares, basis and collateral")
    st.dataframe(pd.DataFrame(result["rows"]), hide_index=True)
    st.caption(
        "Premiums enter cash once. Physical delivery changes shares and separate federal/NJ basis. "
        "Collateral is reserved cash, not an expense. Exhausted cash remains a liability. "
        "Dividend yields price options; only explicit dated dividends enter cash. "
        "Rolls close one priced contract and open another. American assignment dates "
        "are supplied scenarios; QuantLib does not predict a broker's exercise decisions."
    )
    st.dataframe(pd.DataFrame(result["terminations"]), hide_index=True)
    st.dataframe(pd.DataFrame(result["tax"]), hide_index=True)
    if result["failures"]:
        st.error("; ".join(result["failures"]))
    with st.expander("Leg marks, stock/index stress and complete assumptions"):
        st.dataframe(pd.DataFrame(result["legs"]), hide_index=True)
        st.dataframe(pd.DataFrame(result["stress"]), hide_index=True)
        st.json(result)
    st.download_button(
        "Export dated option result",
        json.dumps(result, default=str),
        "synthetic-option-run.json",
        "application/json",
    )
