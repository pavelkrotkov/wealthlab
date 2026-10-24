"""Inspect/export a reusable realized market batch without claiming retirement safety."""

import json

import numpy as np
import pandas as pd
import streamlit as st

from wealthlab.markets.example import synthetic
from wealthlab.markets.inputs import MarketCase
from wealthlab.markets.paths import generate
from wealthlab.markets.report import summarize, terminal_table
from wealthlab.markets.stresses import NAMES
from wealthlab.ui.uploads import invalid, source


def show():
    st.header("Market paths and named stresses")
    st.warning(
        "Path assumptions and buy-and-hold factor diagnostics only. Household lot sales, "
        "tax payments, rebalancing, spending guardrails and employer-linked employment "
        "still need integration. These charts do not measure spending success or after-tax returns."
    )
    st.caption(
        "Rates are decimal fractions. Annual expected mark growth is arithmetic; volatility "
        "and correlation describe log shocks, with inflation last in the matrix. Cash yields "
        "remain separate unless marks explicitly include reinvestment. Historical observations "
        "must cover consecutive complete months available by projection start; no gap filling "
        "or cycling. Named stresses are assumptions with no event probabilities."
    )
    mode = st.selectbox(
        "Synthetic market mode", ["monte_carlo", "deterministic", "historical", "stress"]
    )
    stress = st.selectbox("Synthetic named stress", NAMES)
    uploaded = st.file_uploader("Load market assumptions JSON", type="json")
    if source(uploaded, synthetic(mode, stress).model_dump_json(indent=2), "markets") is None:
        return
    with st.form("markets_case"):
        edited = st.text_area(
            "Market factors, correlations and provenance (JSON)", key="markets_editor", height=400
        )
        submitted = st.form_submit_button("Generate market paths", type="primary")
    if submitted:
        calculate(edited)
    if "markets_result" in st.session_state:
        display(st.session_state["markets_result"])


def calculate(edited):
    try:
        case = MarketCase.model_validate_json(edited or "")
        batch = generate(case)
        report = summarize(batch)
        st.session_state.update(
            markets_result=(batch, report), markets_input=case.model_dump_json(indent=2)
        )
    except ValueError as error:
        invalid(error, "markets")


def display(result):
    batch, report = result
    a, b, c = st.columns(3)
    a.metric("Realized paths", batch.mark_returns.shape[0])
    b.metric("Months per path", len(batch.dates))
    c.metric("Market factors", len(batch.assets))
    st.caption(f"Realized batch: {batch.metadata['batch_id']}")
    st.dataframe(terminal_table(batch, report), hide_index=True, width="stretch")
    identity = st.selectbox("Factor to inspect", batch.assets)
    index = batch.assets.index(identity)
    quantiles = np.quantile(report["mark_indices"][:, :, index], [0.05, 0.50, 0.95], axis=0)
    st.line_chart(
        pd.DataFrame(quantiles.T, index=pd.to_datetime(batch.dates), columns=["p05", "p50", "p95"])
    )
    st.caption(
        "Mark-only index starts at 100 immediately before month one. Cash yields accumulate "
        "separately without interest. Real buy-and-hold value includes that cash and modeled "
        "inflation; fees and taxes are absent. Percentiles describe model paths, not confidence "
        "bounds on a calibrated forecast. Locks retain value while preventing modeled liquidity. "
        "Reuse the exported batch for paired policies; "
        "do not regenerate paths per candidate."
    )
    with st.expander("Reproduction metadata and assumptions"):
        st.json(batch.metadata)
    st.download_button(
        "Export market assumptions",
        st.session_state["markets_input"],
        "market-case.json",
        "application/json",
    )
    st.download_button(
        "Export realized market paths",
        json.dumps(batch.export()),
        "market-paths.json",
        "application/json",
    )
