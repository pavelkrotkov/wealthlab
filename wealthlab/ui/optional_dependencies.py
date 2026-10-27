"""Disclose missing production retirement data before a limited installation runs a profile."""

from importlib.util import find_spec

import streamlit as st


def retirement_notice():
    if find_spec("owlplanner") is None:
        st.info(
            "Limited installation: Social Security entitlement/FRA calculations and applicable "
            "RMD profiles require the pinned Owl tables. Use the recommended full installation "
            "with the benchmarks extra before running those cases; core cash-flow screens "
            "remain available. The extra also enables the independent Owl comparison."
        )
