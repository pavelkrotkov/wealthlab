"""Compare editable policy schedules with actual liquid saving and independently priced cover."""

import streamlit as st

from wealthlab.products.life_comparison import compare
from wealthlab.products.life_comparison_inputs import LifeComparison
from wealthlab.products.life_comparison_markets import synthetic
from wealthlab.ui.life_comparison_results import display
from wealthlab.ui.product_selections import select
from wealthlab.ui.uploads import invalid, source


def show():
    st.subheader("Whole life versus liquid saving and protection")
    st.caption(
        "Match household capital, spending and taxes. Price term cover independently; edit "
        "limited-pay and longer premium schedules, required payment failures and monthly "
        "policy values. The uninsured reference keeps the same independent protection need; "
        "a new-issue preset starts with zero policy value, basis, loan and coverage. "
        "Saving budgets buy actual shares after reserving current bills, tax "
        "and your cash buffer. Policy values remain supplied assumptions on every market path."
    )
    opening = select(
        "Opening policy example",
        ["New policies", "Existing policy with MEC assumption", "No policy versus new issue"],
        key="life_comparison_opening",
    )
    existing = opening == "Existing policy with MEC assumption"
    uninsured = opening == "No policy versus new issue"
    mode = select(
        "Comparison market method",
        ["entered", "deterministic", "historical", "monte_carlo", "stress"],
        key="life_comparison_method",
    )
    namespace = (
        "life_comparison_" + mode + ("_uninsured" if uninsured else "_existing" if existing else "")
    )
    uploaded = st.file_uploader("Load insurance alternatives JSON", type="json")
    if (
        source(uploaded, synthetic(mode, existing, uninsured).model_dump_json(indent=2), namespace)
        is None
    ):
        return
    with st.form(namespace):
        edited = st.text_area(
            "Matched households, policy terms, saving budgets and markets (JSON)",
            key=namespace + "_editor",
            height=450,
        )
        submitted = st.form_submit_button("Compare actual insurance alternatives", type="primary")
    if submitted:
        calculate(edited, namespace)
    if namespace + "_result" in st.session_state:
        display(st.session_state[namespace + "_result"])


def calculate(edited, namespace):
    try:
        result = compare(LifeComparison.model_validate_json(edited))
        st.session_state[namespace + "_result"] = result
        st.session_state[namespace + "_input"] = edited
    except (ValueError, TypeError, KeyError) as error:
        invalid(error, namespace)
