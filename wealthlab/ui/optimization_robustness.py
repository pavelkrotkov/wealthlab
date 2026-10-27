"""Matched replay failures stay visible even when the Monte Carlo hold-out passes."""

import pandas as pd
import streamlit as st


def display(result):
    checks = result["robustness"]
    if not checks:
        st.caption("No additional deterministic, historical or stress checks were configured.")
        return
    st.subheader("Frozen-policy robustness checks")
    st.caption(
        "Selected policy and original baseline share each realized path. Supplied historical "
        "and stress cases are scenarios, not event probabilities. Stochastic stress intervals "
        "are conditional on that named overlay. These results never select a different policy."
    )
    st.dataframe(
        pd.DataFrame([summary(name, item) for name, item in checks.items()]), hide_index=True
    )
    if result["configured_validation_passed"] is False:
        st.warning("The training-selected policy did not pass all configured required validation.")
    with st.expander("Matched robustness cash, taxes, constraints and realized paths"):
        st.json(checks)


def summary(name, item):
    assessment = item.get("selected", {}).get("assessment", {})
    return dict(
        check=name,
        status=item["status"],
        required=item["required"],
        funding_path_fraction=assessment.get("joint_success_fraction"),
        reserve_path_fraction=assessment.get("reserve_success_fraction"),
        real_exit_wealth=assessment.get("median_real_after_tax_exit_wealth"),
        constraints=assessment.get("unmet_constraints"),
        unsupported_reason=item.get("selected", {}).get("unsupported_reason")
        or item.get("baseline", {}).get("unsupported_reason"),
    )
