"""Inspect an independent retirement policy and its actual household replay locally."""

import json
from importlib.util import find_spec

import pandas as pd
import streamlit as st

from wealthlab.retirement.owl_household_inputs import OwlHouseholdCase, synthetic
from wealthlab.retirement.owl_household_reference import SCOPE, run
from wealthlab.ui.uploads import invalid, source


def show():
    st.header("OWL household reference")
    st.info("Independent engine comparison. The source max-bequest policy is not your optimizer.")
    st.caption(SCOPE)
    if find_spec("owlplanner") is None:
        st.info("Install the benchmarks extra to enable this local comparison.")
        return
    uploaded = st.file_uploader("Load OWL household reference JSON", type="json")
    if source(uploaded, synthetic().model_dump_json(indent=2), "owl_reference") is None:
        return
    with st.form("owl_reference_case"):
        edited = st.text_area(
            "Reference balances, spending and scope (JSON)", key="owl_reference_editor", height=400
        )
        submitted = st.form_submit_button("Compare retirement engines", type="primary")
    if submitted:
        try:
            case = OwlHouseholdCase.model_validate_json(edited or "")
            with st.spinner("Solving the source policy and replaying actual household funding…"):
                st.session_state["owl_reference_result"] = run(case)
            st.session_state["owl_reference_input"] = case.model_dump_json(indent=2)
        except ValueError as error:
            invalid(error, "owl_reference")
    if "owl_reference_result" in st.session_state:
        display(st.session_state["owl_reference_result"])


def display(result):
    st.caption("Synthetic inputs" if result["case"]["synthetic"] else "User-entered local inputs")
    left, right = st.columns(2)
    left.metric(
        "Maximum wealth/tax residual · USD", f"${result['max_absolute_wealth_residual']:,.2f}"
    )
    right.metric(
        "Native spending/tax funding failure", "Yes" if result["funding_failure"] else "No"
    )
    st.caption(
        "A small residual reconciles cash accounting; it does not establish matching taxes. "
        "Native tax follows each year's installed package law. "
        f"OWL {result['reference']['version']} assumes OBBBA replacement in "
        f"{result['reference']['assumed_obbba_replacement_year']}. "
        f"Its separate estate proxy is USD {result['reference']['estate_proxy']:,.2f}, "
        f"using a flat heirs-tax assumption of {result['reference']['heirs_tax_rate']}."
    )
    table = pd.DataFrame(result["rows"])
    st.subheader("Annual tax forecast comparison · USD")
    st.dataframe(
        table[
            [
                "year",
                "reference_federal_tax",
                "native_federal_tax",
                "native_nj_tax",
                "cumulative_tax_difference",
                "native_rmd_shortfall",
                "unfilled_ira_requests",
            ]
        ],
        hide_index=True,
        width="stretch",
    )
    st.subheader("Marked nominal wealth · USD")
    wealth = table.set_index("year")[["reference_marked_wealth", "native_marked_wealth"]]
    st.line_chart(wealth.astype(float))
    with st.expander("Full annual balances, spending, deductions and accounting residuals"):
        st.dataframe(table, hide_index=True, width="stretch")
    with st.expander("Source policy, compiled household and monthly audit"):
        st.json(json.dumps(result, default=str))
    st.download_button(
        "Export reference inputs",
        st.session_state["owl_reference_input"],
        "owl-household-case.json",
        "application/json",
    )
    st.download_button(
        "Export full retirement comparison",
        json.dumps(result, default=str, indent=2),
        "owl-household-result.json",
        "application/json",
    )
