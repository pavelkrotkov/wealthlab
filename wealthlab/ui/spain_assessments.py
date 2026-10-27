"""Editable independent annual cases and supplied schedules; actual cash stays separate."""

import streamlit as st

from wealthlab.tax.spain_assessment_example import synthetic_plan
from wealthlab.tax.spain_assessment_inputs import SpainAssessmentPlan
from wealthlab.tax.spain_assessment_plan import evaluate_plan
from wealthlab.ui.spain_assessment_results import display
from wealthlab.ui.uploads import invalid, source


def show():
    st.subheader("Spain: people, annual assessments and tax schedules")
    st.warning(
        "Supply independently classified annual facts and remaining EUR schedules. "
        "Individual cases retain separate caps and payments; their sum is not joint filing. "
        "A scheduled bill is not paid tax. Actual funding, refunds and bilateral credits require "
        "the cross-border cash-flow scenario. Later years use explicit frozen-2025 rules."
    )
    uploaded = st.file_uploader("Load Spain assessment plan JSON", type="json")
    if source(uploaded, synthetic_plan().model_dump_json(indent=2), "spain_assessments") is None:
        return
    with st.form("spain_assessments"):
        edited = st.text_area(
            "Annual classifications, observed payments and remaining tax schedules (JSON)",
            key="spain_assessments_editor",
            height=420,
        )
        submitted = st.form_submit_button(
            "Reconcile annual assessments and schedules", type="primary"
        )
    if submitted:
        calculate(edited)
    if "spain_assessments_result" in st.session_state:
        display(st.session_state["spain_assessments_result"])


def calculate(edited):
    try:
        plan = SpainAssessmentPlan.model_validate_json(edited)
        st.session_state.update(
            spain_assessments_result=evaluate_plan(plan), spain_assessments_input=edited
        )
    except (ValueError, TypeError) as error:
        invalid(error, "spain_assessments")
