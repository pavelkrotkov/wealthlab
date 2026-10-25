"""Actual option cash/basis and conditional recognition accompany household outcomes."""

import json

import pandas as pd
import streamlit as st


def controls(payload, scenario):
    with st.expander("Household options, assignment and collateral"):
        enabled = st.checkbox(
            "Project actual household options", value=scenario.option_plan is not None
        )
        st.caption(
            "Actual premiums, strike delivery and unreserved proceeds use household cash after "
            "prior-tax arrears, before sleeves and deposits. Reserved collateral cannot pay bills. "
            "Resolve federal/NJ tax assumptions first. Each month needs an explicit "
            "dated accounting mark; generated-market option bindings are unfinished."
        )
        if not enabled:
            return None
        if payload.get("option_plan") is None:
            st.warning("Load the synthetic option household or import a complete plan first.")
            return None
        return st.text_area(
            "Household option account, dated contracts and assumptions (JSON)",
            json.dumps(payload["option_plan"], indent=2),
            height=350,
        )


def display(rows):
    if "option_audit" not in rows[-1]:
        return
    st.subheader("Actual household option cash, shares and tax basis")
    st.caption(
        "Account equity is already in household wealth. Only unreserved cash pays spending. "
        "Negative equity remains a separate liability. Recognized gains use the shared "
        "annual federal/NJ engine and actual tax timing; gross losses are not cash savings."
    )
    st.dataframe(pd.DataFrame(rows[-1]["option_audit"]), hide_index=True)
    with st.expander("Actual option recognition and remaining lots"):
        st.json(rows[-1]["option_tax_audit"])
        st.json(rows[-1]["option_lots"])
