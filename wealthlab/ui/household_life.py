"""Show actual policy funding, independent protection need and the dated cash reserve."""

import json

import pandas as pd
import streamlit as st


def controls(payload, scenario):
    with st.expander("Household whole-life contracts and required premium funding"):
        enabled = st.checkbox(
            "Project household whole-life policies", value=bool(payload.get("life_plan"))
        )
        st.caption(
            "Use one USD insurance account per policy, opening net surrender value and complete "
            "post-event monthly values. An explicit empty holdings list retains uninsured needs. "
            "Every required payment needs a supplied, confirmed "
            "failure exit. Cash-only or permitted household-sale funding is explicit. "
            "Missing tax/value terms cannot establish household funding success."
        )
        if not enabled:
            return None
        if payload.get("life_plan") is None:
            st.warning("Load the synthetic whole-life household or import a complete policy plan.")
            return None
        return st.text_area(
            "Policy ownership, values, failure settlements and reserve schedule (JSON)",
            json.dumps(payload["life_plan"], indent=2),
            height=350,
        )


def display(rows):
    if "life_policy_audit" not in rows[-1]:
        return
    st.subheader("Actual whole-life funding and protection")
    ending = rows[-1]
    a, b, c = st.columns(3)
    a.metric("Policy payment shortfalls", f"${sum(r['life_payment_unfunded'] for r in rows):,.2f}")
    b.metric("Dated policy payment reserve", f"${ending['life_reserve_target']:,.2f}")
    c.metric("Uncovered insurance need", f"${ending['life_protection_shortfall']:,.2f}")
    st.caption(
        "Living wealth includes net surrender value once; outstanding loans are already "
        "subtracted there. Death protection is separate. The policy reserve sums actual dated "
        "required payments over the configured reserve window, without annualizing lump premiums. "
        "Failed payments execute only the supplied conditional exit, cancel later events and "
        "retain their funding failure. Policy receipts and withholding share actual annual taxes."
    )
    st.write(
        {
            "Premiums actually paid from retirement": sum(
                r["life_retirement_premiums_paid"] for r in rows
            ),
            "Listed future premiums from retirement": ending["life_future_retirement_premiums"],
        }
    )
    st.dataframe(pd.DataFrame(ending["life_policy_values"]), hide_index=True)
    with st.expander("Policy inputs, actual events and cancelled schedules"):
        st.json(ending["life_policy_audit"])
