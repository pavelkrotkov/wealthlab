"""Expose sourced fees on shared paths with original hypothetical starter rates."""

import streamlit as st

from wealthlab.household.advisory_advance_example import advance_plan
from wealthlab.household.advisory_example import plan


def controls(scenario):
    if not st.checkbox("Add hypothetical outer advisory AUM fees", key="market_advisory_example"):
        return scenario
    st.caption(
        "Original hypothetical marginal rates are editable in the household JSON, not an adviser "
        "quote. Fees use supported observed net-equity bases and the actual shared cash ledger; "
        "Advance bills can use actual stored opening values; daily/first-day payment remains "
        "unsupported. No future valuation or receipt is pulled into an earlier invoice."
    )
    profile = st.selectbox(
        "Hypothetical advisory fee profile",
        ["Observed arrears", "Advance on observed opening"],
        key="market_advisory_profile",
    )
    build = plan if profile == "Observed arrears" else advance_plan
    return scenario.model_copy(update=dict(advisory_fee_plan=build(scenario)))
