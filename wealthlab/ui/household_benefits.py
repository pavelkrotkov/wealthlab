"""Explicit claim inputs alongside the household's existing tax and cash schedules."""

import json

import streamlit as st

from wealthlab.retirement.social_household import template


def controls(payload, scenario):
    with st.expander("Household Social Security claims"):
        enabled = st.checkbox(
            "Include generated Social Security payments",
            value=payload.get("social_security") is not None,
        )
        st.caption(
            "Generated benefits enter cash and the federal benefit calculation once, with no NJ "
            "income or payroll tax. They are not reduced by the household retirement date. "
            "Supply the annual tax plan, matching member IDs/birth dates "
            "and verified PIA/eligibility. "
            "The blank template is unresolved and cannot produce a personal result. "
            "Whole calendar months and survival through the horizon are required here. "
            "Any annual wages with pre-FRA entitlement block this bridge pending the work-test "
            "layer; changing wages cannot silently keep a no-deduction confirmation valid. "
            "Without a Medicare collection plan, payments are before premium offsets. "
            "Select SSA collection in the Medicare plan for supported gross/net accounting. "
            "Income-tax withholding is not generated. Standalone workbench balances "
            "are not additional household cash."
        )
        if not enabled:
            return None
        plan = payload.get("social_security") or template(scenario)
        return st.text_area(
            "Household claim dates, eligibility and PIA (JSON)",
            json.dumps(plan, indent=2),
            height=300,
        )
