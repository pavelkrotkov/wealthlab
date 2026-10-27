"""Editable dated foreign-tax facts show cash, source limits and unresolved scope separately."""

import json

import streamlit as st

from wealthlab.tax.foreign_credit import evaluate
from wealthlab.tax.foreign_credit_example import synthetic
from wealthlab.tax.foreign_credit_inputs import ForeignCreditCase
from wealthlab.ui.uploads import invalid, source


def show():
    st.header("Cross-border tax interactions")
    st.warning(
        "Conditional ordinary US foreign-tax-credit workbench. Person residence, jurisdiction "
        "assessments and household funding require the subsequent interaction profiles."
    )
    st.caption(
        "Paid-tax FX, credit refund reversal and actual refund cash retain independent dates. "
        "Unknown eligibility or currency-income treatment blocks the affected credit result. "
        "The current ordinary general/passive profile uses final2025 forms and explicit "
        "frozen2025 assumptions for later years. Payroll and mainland NJ remain independent "
        "entered baseline facts; no social-insurance coverage or state departure is inferred."
    )
    uploaded = st.file_uploader("Load dated foreign-credit case JSON", type="json")
    if source(uploaded, synthetic().model_dump_json(indent=2), "foreign_credit") is None:
        return
    with st.form("foreign_credit"):
        edited = st.text_area(
            "People, annual facts, source income, tax payments and FX (JSON)",
            key="foreign_credit_editor",
            height=430,
        )
        submitted = st.form_submit_button("Calculate dated foreign tax credit", type="primary")
    if submitted:
        calculate(edited)
    if "foreign_credit_result" in st.session_state:
        display(st.session_state["foreign_credit_result"])


def calculate(edited):
    try:
        case = ForeignCreditCase.model_validate_json(edited)
        result = evaluate(case)
        st.session_state.update(foreign_credit_result=result, foreign_credit_input=edited)
    except (ValueError, KeyError, TypeError) as error:
        invalid(error, "foreign_credit")


def display(result):
    st.write("Credit status", result["credit_status"])
    st.write(
        "Observed current-year foreign tax cash outflow (USD)",
        result["observed_tax_cash_outflow_usd"],
    )
    st.dataframe(result["actual_tax_cash"])
    for reason in result["unresolved"]:
        st.warning(reason)
    if result["candidate"] is not None:
        st.dataframe(
            [
                dict(comparison=label, **items["federal"])
                for label, items in [
                    ("baseline", result["baseline"]),
                    ("conditional credit", result["candidate"]),
                ]
            ]
        )
        st.dataframe(result["basket_audit"])
        st.json(json.dumps(result["carry_audit"], default=str))
    st.caption(
        "A tax credit changes liability. It is not a cash refund or a household funding "
        "result. Original-year revisions, carryback/personal allocation and unsupported "
        "profiles stay explicit; no predicted refund funds a payment."
    )
    st.download_button(
        "Download dated foreign-credit audit",
        json.dumps(result, default=str, indent=2),
        file_name="foreign-credit-audit.json",
        mime="application/json",
    )
