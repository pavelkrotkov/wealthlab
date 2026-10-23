"""Scenario dates, display currency and adjustable planning targets."""

import json

import streamlit as st


def controls(payload: dict) -> None:
    payload["name"] = st.text_input("Scenario name", payload["name"])
    payload["synthetic"] = st.checkbox("Synthetic example", payload["synthetic"])
    left, right = st.columns(2)
    payload["start"] = left.text_input("Start date (inclusive)", payload["start"])
    payload["end"] = right.text_input("End date (exclusive)", payload["end"])
    payload["inflation"] = (
        st.number_input("Reporting inflation (%)", -50.0, 100.0, payload["inflation"] * 100) / 100
    )
    payload["reserve_years"] = st.number_input(
        "Liquid reserve target (years)", 0.0, 20.0, float(payload["reserve_years"])
    )
    with st.expander("Currency, targets and year-to-date context"):
        st.caption(
            "Success and age targets are retained for later simulation/optimization. "
            "This projection uses the explicit end date and reports no success probability."
        )
        fx = st.text_input(
            "USD per unit of currency (JSON)", json.dumps(payload["usd_per_currency"])
        )
        payload["usd_per_currency"] = fx
        payload["target_success"] = (
            st.number_input(
                "Future simulation success target (%)", 1.0, 100.0, payload["target_success"] * 100
            )
            / 100
        )
        payload["target_age"] = st.number_input(
            "Horizon target: younger member age", 50, 120, payload["target_age"]
        )
        for field, value in payload["ytd"].items():
            payload["ytd"][field] = str(
                st.number_input("YTD " + field.replace("_", " "), min_value=0.0, value=float(value))
            )
