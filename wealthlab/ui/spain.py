"""Editable annual regional assessments retain unresolved product and treaty classifications."""

import json

import streamlit as st

from wealthlab.tax.spain import evaluate
from wealthlab.tax.spain_example import synthetic
from wealthlab.tax.spain_inputs import SpainCase
from wealthlab.ui.uploads import invalid, source


def show():
    st.subheader("Spain: annual income and wealth taxes")
    st.warning(
        "Conditional individual full-year resident assessment using published 2025 schedules. "
        "Madrid, Catalonia and Castilla-La Mancha are supported. Supply eligible minima, "
        "post-limitation income and foreign-product/treaty classifications. Unresolved facts "
        "block affected results. Bilateral credits and household funding need separate adapters."
    )
    region = st.selectbox("Synthetic Spanish region", ["castilla_la_mancha", "madrid", "catalonia"])
    uploaded = st.file_uploader("Load Spain annual case JSON", type="json")
    default = synthetic(region).model_dump_json(indent=2)
    if source(uploaded, default, "spain") is None:
        return
    with st.form("spain"):
        edited = st.text_area(
            "Spanish status, recognized facts and fiscal values (JSON)",
            key="spain_editor",
            height=420,
        )
        submitted = st.form_submit_button("Calculate Spanish assessment", type="primary")
    if submitted:
        calculate(edited)
    if "spain_result" in st.session_state:
        display(st.session_state["spain_result"])


def calculate(edited):
    try:
        case = SpainCase.model_validate_json(edited)
        st.session_state.update(spain_result=evaluate(case), spain_input=edited)
    except (ValueError, TypeError) as error:
        invalid(error, "spain")


def display(result):
    st.caption(
        "EUR liabilities are assessments, not cash receipts. Observed payments keep independent "
        "dates, currency translation and recognized tax. Unpaid IP creates no solidarity credit. "
        "The examples are synthetic; no Spanish region, eligibility or move date is inferred."
    )
    for name in ("income", "wealth"):
        section = result[name]
        st.subheader(name.capitalize())
        if section["status"] == "blocked":
            st.error(" ".join(section["reasons"]))
        else:
            st.json(section["assessment"])
    if result["total_liability_eur"] is not None:
        st.metric(
            "Conditional total Spanish liability · EUR", f"€{result['total_liability_eur']:,.2f}"
        )
    st.download_button(
        "Export Spain assessment and inputs",
        json.dumps(result, indent=2, default=str),
        "synthetic-spain-assessment.json",
        "application/json",
    )
    with st.expander("Policy, payments and reproduction details"):
        st.json(result)
