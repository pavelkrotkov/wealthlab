"""Edit native country facts and execute their actual bills through the shared household cash.

People, recognition dates and independent foreign classifications remain
visible in the input. Failed replacements clear the earlier calculation and
exports so a stale favorable cash result cannot survive invalid source facts.
"""

import json

import streamlit as st

from wealthlab.household.scenario import Scenario
from wealthlab.tax.jurisdiction_execution import evaluate
from wealthlab.tax.jurisdiction_execution_example import synthetic
from wealthlab.tax.jurisdiction_execution_facts import JurisdictionExecutionCase
from wealthlab.ui.uploads import invalid, source

PREFIX = "jurisdiction_execution"


def show():
    st.header("Native country assessments and actual household cash")
    st.warning(
        "Conditional ordinary PR or full-year common-regime Spain facts. Legal residence and "
        "source classifications are supplied per person/year. Spanish foreign-credit relief is "
        "explicitly denied in this comparison; unresolved treaty relief blocks execution. "
        "Preferential gains, cross-year redeterminations and unknown foreign funding gains "
        "require their supported dated profiles."
    )
    country = st.radio("Country execution example", ["Puerto Rico", "Spain"])
    uploaded = st.file_uploader("Load country execution JSON", type="json", key=PREFIX + "_upload")
    prefix = PREFIX + ("_pr" if country == "Puerto Rico" else "_es")
    if source(uploaded, synthetic(country).model_dump_json(indent=2), prefix) is None:
        return
    with st.form(prefix):
        edited = st.text_area(
            "Native people/source/assessment facts and shared cash plan (JSON)",
            key=prefix + "_editor",
            height=460,
        )
        submitted = st.form_submit_button("Calculate country assessments and cash", type="primary")
    if submitted:
        calculate(edited, prefix)
    if prefix + "_result" in st.session_state:
        display(*st.session_state[prefix + "_result"])


def calculate(edited, prefix):
    try:
        case = JurisdictionExecutionCase.model_validate_json(edited)
        result = evaluate(case.scenario, spain=case.spain)
        st.session_state.update({prefix + "_result": (case, result), prefix + "_input": edited})
    except (ValueError, KeyError, TypeError) as error:
        invalid(error, prefix)


def display(case, result):
    from wealthlab.ui.results import display as household_display

    household_display(Scenario.model_validate(result["scenario"]), result["rows"])
    st.subheader("Native country assessment and actual paid-tax reconciliation")
    st.json(result["country_assessments"])
    st.caption(
        f"Converged in {len(result['reconciliation'])} bounded checks. Each check starts the "
        "same household; displayed cash belongs only to the final reconciled execution. "
        "Employee payroll, ordinary US tax, independent NJ tax and foreign cash remain separate."
    )
    st.download_button(
        "Export country execution inputs",
        case.model_dump_json(indent=2),
        file_name="country-execution.json",
        mime="application/json",
    )
    st.download_button(
        "Download country execution audit",
        json.dumps(result, default=str, indent=2),
        file_name="country-execution-audit.json",
        mime="application/json",
    )
