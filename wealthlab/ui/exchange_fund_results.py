"""Expose cash failures beside locked wealth and retain the full source/lot audit."""

import json

import streamlit as st


def display(result):
    policy_disclosure(result)
    st.dataframe([dict(policy=name, **values) for name, values in result["outcomes"].items()])
    for name, rows in result["rows"].items():
        st.write(name)
        st.dataframe(
            [
                {
                    key: value
                    for key, value in row.items()
                    if (key.startswith("exchange_") and key != "exchange_fund_audit")
                    or key
                    in {
                        "date",
                        "closing_cash",
                        "net_wealth",
                        "funding_shortfall",
                        "funding_failure",
                        "tax_unfunded",
                        "tax_position",
                    }
                }
                for row in rows
            ]
        )
        with st.expander(f"{name} actual lots, taxes and contract audit"):
            st.json(rows[-1]["exchange_fund_audit"])
    st.download_button(
        "Download complete exchange comparison",
        json.dumps(result, default=str, indent=2),
        file_name="exchange-fund-comparison.json",
        mime="application/json",
    )


def policy_disclosure(result):
    if result.get("fund_specific_exclusions_confirmed"):
        st.warning(
            "Explicit policy difference: fund cash/K-1/basis inputs are excluded from "
            "direct shares and itemized in the monthly audit. Direct redeem requests "
            "acknowledge already owned basket shares; sell_liquid raises actual cash."
        )
