"""Editable sourced home marks/close terms and actual property/debt/cash evidence."""

import json

import pandas as pd
import streamlit as st

from wealthlab.household.report import encode


def controls(payload, scenario):
    with st.expander("Sourced property/home and actual linked debt payoff"):
        st.caption(
            "Unmodeled property accounts keep opening marks and cannot be sold. The native "
            "personal-home book needs complete USD month-end values, lien IDs and supplied "
            "independent tax recognition. Rental, changing basis, inferred residence exclusions, "
            "closing withholding and deductible linked mortgage interest need other adapters. "
            "Gross escrow funds pay all costs/liens before net proceeds reach the cash pool. "
            "Negative-equity closes require existing authorized owner cash; blocked requests "
            "leave property, live debt and contingent tax/cost unposted."
        )
        if not st.checkbox(
            "Use a complete sourced property book",
            value=scenario.property_plan is not None,
            key="property_enabled",
        ):
            return None
        return st.text_area(
            "Property marks, retention/sale and source facts (JSON)",
            json.dumps(payload.get("property_plan") or {}, indent=2),
            height=400,
            key="property_editor",
        )


def display(rows):
    audit = rows[-1].get("property_audit")
    if audit is None:
        return
    st.subheader("Actual property, liens and closing cash")
    st.caption(
        "Retained equity is marked wealth, not liquid spending cash. Sale occurs only at the "
        "declared month end. Successful closes pay existing native debt principal/full-month "
        "interest once; blocked closes retain normal debt service. No sale proceeds, tax "
        "exclusion or mortgage-interest deduction is invented. Inspect independently supplied "
        "tax amounts and all unresolved source assumptions before using a result."
    )
    st.dataframe(pd.DataFrame(audit["economic_state"]), hide_index=True)
    with st.expander("Property close, native debt and source audit"):
        st.json(encode(audit))
