"""Funding sampling intervals and product feasibility concern different constraints."""

import streamlit as st

from wealthlab.ui.household_sleeves import feasibility


def display(result):
    totals = result["aggregate"]
    a, b, c = st.columns(3)
    a.metric("Funded paths / supplied horizon", f"{totals['successes']} / {totals['paths']}")
    b.metric("Simulated funding fraction", f"{totals['funding_fraction']:.1%}")
    c.metric("Covers entire target age", "Yes" if totals["horizon_covers_target_age"] else "No")
    feasibility(result)
    interval = totals["monte_carlo_95_wilson"]
    if interval is not None:
        st.caption(
            f"95% Wilson interval for simulated funding: {interval[0]:.1%} to {interval[1]:.1%}. "
            "Sampling uncertainty conditional on this model; "
            "not uncertainty in market or tax assumptions."
        )
