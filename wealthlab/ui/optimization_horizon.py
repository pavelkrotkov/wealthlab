"""Synthetic horizon inputs populate complete schedules; private scenario imports stay separate."""

import streamlit as st

from wealthlab.optimization.horizon_example import synthetic


def show():
    cash = st.number_input("Opening cash (synthetic)", min_value=0, value=2000000, step=100000)
    wages = st.number_input("Monthly W-2 wages (synthetic)", min_value=0, value=5000, step=1000)
    spending = st.number_input(
        "Monthly essential spending (synthetic)", min_value=0, value=2000, step=500
    )
    age = st.number_input("Younger member target age", min_value=50, max_value=120, value=100)
    try:
        case = synthetic(cash=cash, wages=wages, spending=spending, target_age=age)
    except ValueError as error:
        st.error(str(error))
        st.stop()
    st.caption(
        f"Complete calendar years through {case.household.end.year - 1}; income stops at each "
        "selected retirement date and essential spending follows the same inflation paths. "
        "All future tax years explicitly freeze 2025 rules. Cash earns no modeled interest. "
        "The small 4-path training / 8-path validation samples demonstrate execution; they "
        "do not establish a reliable retirement-success probability. "
        "Edit choices and samples below."
    )
    return case
