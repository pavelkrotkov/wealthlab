"""Editable allowed policy grids with distinct search and held-out results."""

import streamlit as st

from wealthlab.optimization.account_example import extend as with_accounts
from wealthlab.optimization.allocation_example import extend as with_allocations
from wealthlab.optimization.diversification_example import extend as with_diversification
from wealthlab.optimization.example import synthetic
from wealthlab.optimization.inputs import PolicySearch
from wealthlab.optimization.life_example import extend as with_life_paths
from wealthlab.optimization.product_example import extend as with_products
from wealthlab.optimization.robustness_example import synthetic as robust
from wealthlab.optimization.search import search
from wealthlab.ui.optimization_horizon import show as horizon_starter
from wealthlab.ui.optimization_results import display
from wealthlab.ui.uploads import invalid, source


def show():
    st.subheader("Bounded policy search")
    st.caption(
        "Set finite allowed choices and lock any dimension. Search retirement dates, native "
        "sale/harvest schedules, IRA/workplace contributions and withdrawals, HSA cash, "
        "529 deposits, saving allocations, rebalancing, taxable funding order and "
        "discretionary guardrails. All choices share capital, essential spending and tax facts. "
        "Fixed products use actual exits; new sleeve mixes use existing cash and supplied unit "
        "schedules. Life choices use complete supplied premium/event/value paths; other product "
        "allocation and cross-border controls remain in progress."
    )
    st.info(
        "Defaults: 95% modeled funding success, through age 100 of the younger member, and "
        "two years of cash reserves. The short synthetic example intentionally fails the "
        "horizon constraint. Supply complete annual/market/account schedules for a longer run."
    )
    starter = starter_case()
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


def starter_case():
    example = st.selectbox(
        "Synthetic starter", ["Short composable examples", "Full age-100 cash and stock example"]
    )
    if example == "Full age-100 cash and stock example":
        return horizon_starter()
    checks = st.checkbox("Add synthetic deterministic, historical and stress checks")
    starter = robust() if checks else synthetic()
    for label, extend in (
        ("Add synthetic workplace, HSA and 529 policies", with_accounts),
        ("Add synthetic stock/bond diversification policies", with_diversification),
        ("Add synthetic conditional products with actual exits", with_products),
        ("Add synthetic cash-funded sleeve allocation choices", with_allocations),
        ("Add synthetic complete life-policy funding paths", with_life_paths),
    ):
        if st.checkbox(label):
            starter = extend(starter)
    return starter


def calculate(edited):
    try:
        case = PolicySearch.model_validate_json(edited)
        progress = st.progress(0.0, text="Evaluating the allowed training grid")
        result = search(
            case,
            path_progress=lambda phase, done, total: progress.progress(
                done / total, text=f"{phase}: {done}/{total} paths"
            ),
        )
        progress.empty()
        st.session_state["policy_search_result"] = result
        st.session_state["policy_search_input"] = edited
    except (ValueError, TypeError, KeyError) as error:
        invalid(error, "policy_search")
