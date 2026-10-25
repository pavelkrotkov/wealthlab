"""Editable allowed policy grids with distinct search and held-out results."""

import streamlit as st

from wealthlab.optimization.example import synthetic
from wealthlab.optimization.inputs import PolicySearch
from wealthlab.optimization.robustness_example import synthetic as robust
from wealthlab.optimization.search import search
from wealthlab.ui.optimization_results import display
from wealthlab.ui.uploads import invalid, source


def show():
    st.subheader("Bounded policy search")
    st.caption(
        "Set finite allowed choices and lock any dimension. Search retirement dates, native "
        "sale/harvest schedules, IRA withdrawals/conversions, taxable funding order and "
        "discretionary guardrails. All choices share capital, essential spending and tax facts. "
        "Product allocations and cross-border search integration are still being built."
    )
    st.info(
        "Defaults: 95% modeled funding success, through age 100 of the younger member, and "
        "two years of cash reserves. The short synthetic example intentionally fails the "
        "horizon constraint. Supply complete annual/market/account schedules for a longer run."
    )
    include_checks = st.checkbox("Add synthetic deterministic, historical and stress checks")
    starter = robust() if include_checks else synthetic()
    uploaded = st.file_uploader("Load policy search JSON", type="json")
    if source(uploaded, starter.model_dump_json(indent=2), "policy_search") is None:
        return
    with st.form("policy_search"):
        edited = st.text_area(
            "Allowed policies, locks, targets and market samples (JSON)",
            key="policy_search_editor",
            height=450,
        )
        submitted = st.form_submit_button("Search allowed policies", type="primary")
    if submitted:
        calculate(edited)
    if "policy_search_result" in st.session_state:
        display(st.session_state["policy_search_result"])


def calculate(edited):
    try:
        case = PolicySearch.model_validate_json(edited)
        progress = st.progress(0.0, text="Evaluating the allowed training grid")
        result = search(case, lambda done, total: progress.progress(done / total))
        progress.empty()
        st.session_state["policy_search_result"] = result
        st.session_state["policy_search_input"] = edited
    except (ValueError, TypeError, KeyError) as error:
        invalid(error, "policy_search")
