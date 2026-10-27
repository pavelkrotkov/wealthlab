"""Editable allowed policy grids with distinct search and held-out results."""

import streamlit as st

from wealthlab.optimization.report import loads, payload
from wealthlab.optimization.search import search
from wealthlab.ui.optimization_results import display
from wealthlab.ui.optimization_starters import show as starter_case
from wealthlab.ui.uploads import invalid, source


def show():
    st.subheader("Bounded policy search")
    st.caption(
        "Set finite allowed choices and lock any dimension. Search retirement dates, native "
        "sale/harvest schedules, IRA/workplace contributions and withdrawals, HSA cash, "
        "529 deposits, saving allocations, rebalancing, taxable funding order and "
        "discretionary guardrails. All choices share capital, essential spending and tax facts. "
        "Fixed products use actual exits; new sleeve mixes use existing cash and supplied unit "
        "schedules. New option units buy actual shares from existing cash. Fixed options "
        "and employer awards require actual contractual exits. Exchange choices retain the "
        "original source shares and basis. "
        "Life choices use complete supplied premium/event/value paths, including new policies "
        "funded by actual future premiums. Common sourced advisory fee contracts use each "
        "candidate's actual native account values and cash; fee assumptions are not choices. "
        "Drilling choices require complete supplied profiles and an independent envelope "
        "valid for all candidates; full-tax drilling optimization is unsupported. "
        "QOZ choices retain source stock and shared eligibility assumptions; actual source "
        "sales, subscriptions, tax revisions and stock settlement execute natively. "
        "Dependent employment and compensation profiles must match retirement dates exactly; "
        "fixed former-employer rights need explicit sourced independence. "
        "Cross-border controls remain in progress."
    )
    st.info(
        "Defaults: 95% modeled funding success, through age 100 of the younger member, and "
        "two years of cash reserves. The short synthetic example intentionally fails the "
        "horizon constraint. Supply complete annual/market/account schedules for a longer run."
    )
    try:
        starter = starter_case()
    except (ValueError, TypeError, KeyError) as error:
        invalid(error, "policy_search_starter")
        return
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
        case = loads(edited)
        progress = st.progress(0.0, text="Evaluating the allowed training grid")
        result = search(
            case,
            path_progress=lambda phase, done, total: progress.progress(
                done / total, text=f"{phase}: {done}/{total} paths"
            ),
        )
        progress.empty()
        st.session_state["policy_search_result"] = payload(result)
        st.session_state["policy_search_input"] = edited
    except (ValueError, TypeError, KeyError) as error:
        invalid(error, "policy_search")
