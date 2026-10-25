"""The hold control removes decisions without changing markets or funding permissions."""

import streamlit as st

from wealthlab.markets.rebalance_example import hold


def controls():
    if st.session_state.get("market_account_scope") == "Taxable rebalancing":
        st.checkbox("Compare matched buy-and-hold policy", value=True, key="rebalance_compare")
        st.caption(
            "The control keeps the same household and market paths, removing only rebalances."
        )


def policy_text(household, raw):
    enabled = st.session_state.get(
        "market_account_scope"
    ) == "Taxable rebalancing" and st.session_state.get("rebalance_compare", False)
    if not enabled:
        return raw
    if raw.strip():
        raise ValueError("Choose automatic hold control or supplied paired JSON, not both.")
    return hold(household).model_dump_json()
