"""Edit and execute foreign tax cash through the same household projection and wallet."""

import json

import streamlit as st

from wealthlab.household.projection import project
from wealthlab.household.scenario import Scenario
from wealthlab.tax.foreign_tax_example import synthetic
from wealthlab.ui.uploads import invalid, source


def show():
    st.header("Actual household foreign-tax cash")
    st.warning(
        "Supplied conditional assessments and ordinary US credit profiles. Country residence, "
        "PR/Spanish assessment adapters and later original-return redetermination remain "
        "separate work. Unknown foreign gain/source/basis prevents a funding-success conclusion."
    )
    st.caption(
        "One wallet pays required foreign taxes before optional products/saving. Native USD/EUR "
        "liabilities and dated quotes stay separate from actual payments, withholding, refunds "
        "and native US credit order. Payroll and independent mainland NJ stay visible."
    )
    uploaded = st.file_uploader("Load foreign-tax household JSON", type="json")
    if source(uploaded, synthetic().model_dump_json(indent=2), "foreign_tax_household") is None:
        return
    with st.form("foreign_tax_household"):
        edited = st.text_area(
            "Household, assessments, actual source links and dated FX (JSON)",
            key="foreign_tax_household_editor",
            height=430,
        )
        submitted = st.form_submit_button("Execute shared foreign tax cash", type="primary")
    if submitted:
        calculate(edited)
    if "foreign_tax_household_result" in st.session_state:
        scenario, rows = st.session_state["foreign_tax_household_result"]
        from wealthlab.ui.results import display

        display(scenario, rows)
        st.download_button(
            "Export foreign-tax household inputs",
            scenario.model_dump_json(indent=2),
            file_name="foreign-tax-household.json",
            mime="application/json",
        )
        st.download_button(
            "Download foreign-tax household audit",
            json.dumps(rows, default=str, indent=2),
            file_name="foreign-tax-household-audit.json",
            mime="application/json",
        )


def calculate(edited):
    try:
        case = Scenario.model_validate_json(edited)
        if case.foreign_tax_plan is None:
            raise ValueError("The foreign-tax workbench requires its shared cash plan.")
        rows = project(case)
        st.session_state.update(
            foreign_tax_household_result=(case, rows), foreign_tax_household_input=edited
        )
    except (ValueError, KeyError, TypeError) as error:
        invalid(error, "foreign_tax_household")


def controls(payload, scenario):
    with st.expander("Foreign assessments, payments/refunds, source withholding and US credits"):
        enabled = st.checkbox(
            "Execute shared foreign-tax cash", value=bool(scenario.foreign_tax_plan)
        )
        st.caption(
            "Required foreign tax precedes optional products/saving. Supply actual monthly "
            "USD/EUR quotes, independent country assessments and source classifications."
        )
        if not enabled:
            return None
        if payload.get("foreign_tax_plan") is None:
            st.warning("Load the synthetic foreign-tax household or import a complete plan.")
            return None
        return st.text_area(
            "Foreign assessments and actual cash execution plan (JSON)",
            json.dumps(payload["foreign_tax_plan"], indent=2),
            height=350,
        )
