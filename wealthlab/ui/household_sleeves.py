"""Explicit sleeve cash, debt and supplied tax recognition sit beside household outcomes."""

import json

import pandas as pd
import streamlit as st


def controls(payload, scenario):
    with st.expander("Household long-short sleeves and supplied tax allocations"):
        enabled = st.checkbox(
            "Project household long-short sleeves", value=payload.get("sleeve_plan") is not None
        )
        st.caption(
            "Collateral uses actual cash after receipts/prior-tax arrears, "
            "before optional wrapper deposits. "
            "Negative equity survives as recourse debt. All recognition is supplied separately; "
            "trade P&L does not establish deductible loss, basis or complete-exit tax. "
            "The synthetic allocations are fixed illustrations, independent of market returns."
        )
        if not enabled:
            return None
        plan = payload.get("sleeve_plan")
        if plan is None:
            st.warning(
                "Load the synthetic sleeve household or import a complete sleeve plan first."
            )
            return None
        return st.text_area(
            "Sleeve contracts, dated observations and tax allocations (JSON)",
            json.dumps(plan, indent=2),
            height=350,
        )


def display(rows):
    if "sleeve_positions" not in rows[-1]:
        return
    st.subheader("Long-short household cash and recourse debt")
    a, b, c = st.columns(3)
    a.metric("Remaining negative-equity liability", f"${rows[-1]['sleeve_liability']:,.2f}")
    b.metric("Margin-policy failure months", sum(bool(r["sleeve_failure"]) for r in rows))
    c.metric("Actual redemption cash", f"${sum(r['sleeve_redemptions'] for r in rows):,.2f}")
    st.caption(
        "Positive equity is already in household account balances. Negative equity is a separate "
        "liability subtracted once; the financing loan inside positive equity "
        "is not subtracted again. "
        "Unpaid required margin is a policy failure, separate from consumption shortfalls. "
        "Taxes use supplied allocations, not inferred strategy tax benefits. Basis, automatic "
        "trade recognition and validated after-tax exit classification remain separate work. "
        "Factor exposures do not identify underlying issuers; missing opening and levered "
        "positions remain unknown for concentration checks."
    )
    st.dataframe(pd.DataFrame(rows[-1]["sleeve_positions"]), hide_index=True, width="stretch")
    with st.expander("Household sleeve cash and economic audit"):
        st.json(rows[-1].get("sleeve_audit", []))
