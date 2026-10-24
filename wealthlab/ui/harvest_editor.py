"""Optional overrides preserve imported case settings unless the user explicitly changes them."""

import json

import streamlit as st


def inputs():
    with st.expander("Harvesting comparison and hypothetical exit"):
        policies = st.text_area("Harvest policies override (JSON; blank uses case)", "")
        comparison = st.selectbox(
            "Harvest comparison",
            ["Use case JSON", "Compare on/off", "Single run"],
            key="harvest_comparison_override",
        )
        exit_mode = st.selectbox(
            "Terminal exit",
            ["Use case JSON", "No terminal exit", "Use settings below"],
            key="terminal_exit_override",
        )
        accounts = st.text_input("Taxable exit account IDs (comma separated)")
        fee = st.number_input("Exit commission per security/account · USD", 0.0, value=0.0)
        clear = st.checkbox("Assume no substantially-identical purchases for 30 days after exit")
        st.caption(
            "Unconfirmed exit loss windows stay pending. Locked positions remain unsold. "
            "Tax differences are annual liabilities; no tax-saving reinvestment is assumed."
        )
    return policies, comparison, exit_mode, accounts, fee, clear


def apply(payload, values):
    policies, comparison, exit_mode, accounts, fee, clear = values
    if policies.strip():
        payload["harvest_policies"] = json.loads(policies)
    if comparison != "Use case JSON":
        payload["compare_harvesting"] = comparison == "Compare on/off"
    if exit_mode == "No terminal exit":
        payload["terminal_exit"] = None
    elif exit_mode == "Use settings below":
        payload["terminal_exit"] = dict(
            account_ids=[key.strip() for key in accounts.split(",") if key.strip()],
            commission_per_trade=fee,
            no_replacements_next30_days=clear,
        )
