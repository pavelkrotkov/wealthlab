"""Durable non-widget product choices survive Streamlit workspace cleanup."""

import streamlit as st

from wealthlab.markets.stresses import NAMES


def select(label, choices, key, *, default=None, disabled=False):
    saved = st.session_state.get(f"{key}_saved", default or choices[0])
    if saved not in choices:
        saved = choices[0]
    chosen = st.selectbox(label, choices, index=choices.index(saved), key=key, disabled=disabled)
    st.session_state[f"{key}_saved"] = chosen
    return chosen


def long_short():
    modes = ["deterministic", "monte_carlo", "historical", "stress"]
    names = [*NAMES, "short_squeeze"]
    mode = select("Product market mode", modes, "product_market_mode")
    stress = select(
        "Product named stress",
        names,
        "product_named_stress",
        disabled=mode != "stress",
    )
    return mode, stress
