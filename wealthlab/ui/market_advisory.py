"""Expose sourced fees on shared paths with original hypothetical starter rates."""

import streamlit as st

from wealthlab.household.advisory_example import plan


def controls(scenario):
    if not st.checkbox("Add hypothetical outer advisory AUM fees", key="market_advisory_example"):
        return scenario
    st.caption(
        "Original hypothetical marginal rates are editable in the household JSON, not an adviser "
        "quote. Fees use supported observed net-equity bases and the actual shared cash ledger; "
        "HSA/529 closing bases and advance billing need another valuation-stage profile."
    )
    return scenario.model_copy(update=dict(advisory_fee_plan=plan(scenario)))
