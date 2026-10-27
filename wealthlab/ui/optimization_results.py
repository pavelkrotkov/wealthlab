"""Expose infeasible constraints, finite search coverage and untouched validation outcomes."""

import json

import pandas as pd
import streamlit as st

from wealthlab.household.report import encode
from wealthlab.ui.optimization_robustness import display as robustness


def display(result):
    st.subheader("Evaluated policy choices")
    st.caption(
        f"Evaluated {result['evaluated_candidates']} of {result['grid_candidates']} allowed "
        "combinations. This is the best evaluated feasible candidate, not a global optimum. "
        "Sampling intervals measure Monte Carlo sampling uncertainty, not model correctness. "
        "Advisory columns distinguish actual assessments, paid cash and ending debt. "
        "All candidates retain the same sourced fee contract and observe their own native "
        "balances; no precomputed AUM or optional zero-fee contract is substituted."
    )
    frame = pd.DataFrame(result["candidates"])
    st.dataframe(frame, hide_index=True)
    selected(result)
    robustness(result)
    with st.expander("Reproduce inputs, selected household, realized paths and tax/cash audit"):
        st.json(encode(result))
    st.download_button(
        "Export policy search inputs",
        json.dumps(result["inputs"], indent=2),
        "policy-search-inputs.json",
        "application/json",
    )
    st.download_button(
        "Export policy search audit",
        encode(result),
        "policy-search-audit.json",
        "application/json",
    )
    st.download_button(
        "Export candidate outcomes",
        frame.to_csv(index=False),
        "policy-search-outcomes.csv",
        "text/csv",
    )


def selected(result):
    if result["selection"] is None:
        st.warning("No evaluated candidate satisfies every target and supported-exit constraint.")
        return
    st.write("Training-selected policy:", result["selection"])
    held_out = result["held_out"]
    st.subheader("Separate validation sample — selection remains frozen")
    st.json(encode(held_out["assessment"]))
    if held_out["assessment"]["eligible"]:
        st.success("The selected candidate also meets the targets on the held-out sample.")
    else:
        st.warning(
            "The selected candidate fails held-out validation. No runner-up was substituted."
        )
    if held_out["results"] is None:
        return
    st.download_button(
        "Export selected country input snapshot"
        if held_out["results"].get("country_context")
        else "Export selected household",
        json.dumps(selected_inputs(held_out["results"]), indent=2),
        "selected-household.json",
        "application/json",
    )


def selected_inputs(results):
    if results.get("country_context"):
        return results["details"][0]["country_inputs"]
    return results["household"]
