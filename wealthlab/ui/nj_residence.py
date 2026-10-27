"""Edit legal NJ periods/source rows and execute actual shared household cash.

The annual view exposes independently identified resident/nonresident returns;
the household view uses the same case inside the actual domestic/foreign cash
ledger. Invalid replacement inputs clear the earlier result and export state,
so an old favorable calculation cannot survive a failed legal/source edit.
"""

import json

import streamlit as st

from wealthlab.household.projection import project
from wealthlab.household.scenario import Scenario
from wealthlab.tax.annual import AnnualCase, evaluate
from wealthlab.tax.nj_residence_example import household_example, synthetic
from wealthlab.ui.uploads import invalid, source


def show():
    st.header("NJ residence and dated source income")
    st.warning(
        "Conditional legal residence facts are supplied per person. Travel or a December "
        "address does not establish domicile. Worldwide US tax and payroll remain separate. "
        "PR/Spain assessments and treaty coordination are subsequent integration work."
    )
    mode = st.radio("NJ residence calculation", ["Annual returns", "Household cash"])
    prefix = "nj_residence_annual" if mode == "Annual returns" else "nj_residence_household"
    case = synthetic() if mode == "Annual returns" else household_example()
    uploaded = st.file_uploader("Load NJ residence JSON", type="json", key=prefix + "_upload")
    if source(uploaded, case.model_dump_json(indent=2), prefix) is None:
        return
    with st.form(prefix):
        edited = st.text_area(
            "People, legal periods and independent NJ source facts (JSON)",
            key=prefix + "_editor",
            height=430,
        )
        submitted = st.form_submit_button("Calculate NJ residence and cash", type="primary")
    if submitted:
        calculate(edited, mode, prefix)
    if prefix + "_result" in st.session_state:
        display(*st.session_state[prefix + "_result"], mode)


def calculate(edited, mode, prefix):
    try:
        case = (AnnualCase if mode == "Annual returns" else Scenario).model_validate_json(edited)
        result = evaluate(case) if isinstance(case, AnnualCase) else project(case)
        st.session_state.update({prefix + "_result": (case, result), prefix + "_input": edited})
    except (ValueError, KeyError, TypeError) as error:
        invalid(error, prefix)


def display(case, result, mode):
    if mode == "Annual returns":
        from wealthlab.ui.tax_results import display as annual_display

        annual_display(case, result)
        state = result["new_jersey"]
    else:
        from wealthlab.ui.results import display as household_display

        household_display(case, result)
        state = result[-1]["annual_tax"]["new_jersey"]
    st.subheader("Separate NJ return identities and actual allocated payments")
    st.dataframe(state.get("residence_returns", []), hide_index=True, width="stretch")
    st.caption(
        "Resident-period income and nonresident NJ-source income use distinct returns. "
        "The nonresident percentage uses worldwide period income and may exceed 100%. "
        "This cash profile uses positive year-end settlement; unallocated NJ withholding, "
        "overpayments/refunds, special deductions and retirement exclusions are unsupported."
    )
    st.download_button(
        "Download NJ residence cash audit",
        json.dumps(result, default=str, indent=2),
        file_name="nj-residence-audit.json",
        mime="application/json",
    )
