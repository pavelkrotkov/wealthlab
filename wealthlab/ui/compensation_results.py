"""Expose contingent value, locked value and optional cash requests without inventing liquidity."""

import pandas as pd
import streamlit as st

from wealthlab.employment.compensation_exit_state import from_rows


def display(rows):
    last = rows[-1]
    if "employer_vested" not in last:
        return
    st.subheader("Employer-linked value and liquidity")
    vested, contingent, locked = st.columns(3)
    vested.metric("Vested employer value", f"${last['employer_vested']:,.2f}")
    contingent.metric("Unvested contingent value", f"${last['employer_unvested_contingent']:,.2f}")
    locked.metric("Locked vested value", f"${last['employer_locked_vested']:,.2f}")
    not_paid = sum(r["employer_distribution_not_paid"] for r in rows)
    st.caption(
        f"Employer exposure is {last['employer_share_of_assets_plus_contingent']:.2%} "
        "of gross marked assets plus contingent value. "
        f"Unpaid optional distribution requests total ${not_paid:,.2f}; actual spending "
        "shortfalls remain in the household funding result. Tax results use supplied "
        "allocations and cash rights. Basis and hypothetical exit tax remain unmodeled."
    )
    termination_evidence(rows)
    with st.expander("Employer value path"):
        columns = ["employer_vested", "employer_unvested_contingent", "employer_locked_vested"]
        st.line_chart(pd.DataFrame(rows).set_index("date")[columns].astype(float))


def termination_evidence(rows):
    evidence = from_rows(rows) or {}
    records = []
    for tranche, item in evidence.items():
        if item is None:
            continue
        records.append(
            dict(
                tranche=tranche,
                termination_status=item.get("termination_status", "unresolved"),
                remaining_units=item.get("contract_units"),
                deferred_value=item.get("separate_deferred_value"),
                cash_due=item.get("remaining_contract_cash_due"),
                reason="; ".join(
                    item.get("termination_reasons", ["No supplied termination facts."])
                ),
            )
        )
    if records:
        st.subheader("Employer contractual exit evidence")
        st.dataframe(pd.DataFrame(records), hide_index=True)
        st.caption(
            "Closure is conditional on supplied source facts and actual balances at the event. "
            "Zero market value alone does not establish termination. "
            "Tax settlement remains separate; "
            "the dated cash and supplied tax allocations still affect household results."
        )
