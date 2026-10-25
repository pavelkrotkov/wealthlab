"""Edit sourced outer fee schedules and distinguish assessment, payment and remaining liability."""

import json

import pandas as pd
import streamlit as st

from wealthlab.household.advisory_example import plan


def controls(payload, scenario):
    with st.expander("Outer advisory AUM fees and actual cash payment"):
        if not st.checkbox(
            "Assess sourced outer advisory fees",
            value=scenario.advisory_fee_plan is not None,
            key="advisory_enabled",
        ):
            return None
        st.caption(
            "Use explicit sources, dated accrual periods, day counts and marginal AUM tiers. "
            "Original defaults are hypothetical, not an adviser quote. Each bill uses current "
            "supported net account equity or sourced native life net-cash/net-surrender values, "
            "after product marks and before optional saving/deposits. Embedded costs remain "
            "separate. Unpaid fees remain liabilities; no automatic tax deduction is claimed. "
            "Cash payments use the complete listed household cash pool in its existing order. "
            "Explicit snapshot cutoffs can use actual opening or prior completed values, "
            "including native HSA/529 net equity. Current HSA/529 closing values are unavailable "
            "at the earlier product stage. Advance billing needs source-confirmed "
            "nonrefundable/no-proration terms; daily/first-day billing is unsupported."
        )
        default = payload.get("advisory_fee_plan") or plan(scenario).model_dump(mode="json")
        return st.text_area(
            "Sourced advisory schedules, tiers and coverage (JSON)",
            json.dumps(default, indent=2),
            height=350,
            key="advisory_editor",
        )


def display(rows):
    audit = rows[-1].get("advisory_fee_audit")
    if audit is None:
        return
    st.subheader("Outer advisory assessments and actual fee cash")
    st.caption(
        "All simultaneous schedules share one observed snapshot. Marginal tiers apply only "
        "to their own AUM bands. Days equal exclusive accrual end minus accrual start; no monthly "
        "fraction or deduction is inferred. Reserved cash still belongs to the household. "
        "Opening/completed snapshots are observed before billing; future dates are blocked. "
        "Month-end payment is never relabeled as first-day cash. "
        "Assessments create a bill, not a product trade or basis adjustment. Existing arrears "
        "precede new fees; the audit distinguishes actual advisory payment from generic fees."
    )
    fields = [
        "date",
        "advisory_fees_assessed",
        "advisory_fees_paid",
        "advisory_fees_owed",
        "fees_owed",
    ]
    st.dataframe(pd.DataFrame(rows)[fields], hide_index=True, width="stretch")
    with st.expander("Sourced fee bases, marginal bands and payment audit"):
        st.json(audit)
