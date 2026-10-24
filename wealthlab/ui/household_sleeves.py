"""Explicit sleeve cash, debt and supplied tax recognition sit beside household outcomes."""

import json

import pandas as pd
import streamlit as st

from wealthlab.ui.sleeve_loss_assumptions import display as loss_results


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
            "The synthetic allocations are fixed illustrations, independent of market returns. "
            "Negative allocations require separate federal/NJ allowed, denied or deferred choices; "
            "allowed/released amounts require explicit eligibility-after-limits assumptions."
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
    b.metric("Unresolved margin months", sum(bool(r.get("sleeve_margin_unresolved")) for r in rows))
    c.metric("Actual redemption cash", f"${sum(r['sleeve_redemptions'] for r in rows):,.2f}")
    st.caption(
        "Positive equity is already in household account balances. Negative equity is a separate "
        "liability subtracted once; the financing loan inside positive equity "
        "is not subtracted again. "
        "A configured liquidation can resolve a margin call. Negative equity and blocked exits "
        "are separate constraints; cash-funding success uses actual unpaid bills/taxes. "
        "Taxes use supplied allocations, not inferred strategy tax benefits. Basis, automatic "
        "trade recognition and validated after-tax exit classification remain separate work. "
        "Factor exposures do not identify underlying issuers; missing opening and levered "
        "positions remain unknown for concentration checks."
    )
    st.write(
        {
            "Negative-equity months": sum(bool(r.get("sleeve_negative_equity")) for r in rows),
            "Blocked requested exits": sum(bool(r.get("sleeve_exit_blocked")) for r in rows),
        }
    )
    st.dataframe(pd.DataFrame(rows[-1]["sleeve_positions"]), hide_index=True, width="stretch")
    loss_results(rows)
    with st.expander("Household sleeve cash and economic audit"):
        st.json(rows[-1].get("sleeve_audit", []))


def feasibility(result):
    if not result["binding"].get("sleeves"):
        return
    totals = result["aggregate"]
    st.caption(
        f"Product-feasible paths: {totals['product_feasible_paths']} / {totals['paths']}; "
        f"joint cash/product feasibility: {totals['joint_feasibility_fraction']:.1%}. "
        "Funding fraction above concerns cash bills/taxes. Product feasibility separately "
        "requires no unresolved margin, negative equity or blocked requested terminal exit."
    )
