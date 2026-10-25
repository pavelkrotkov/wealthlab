"""Edit sourced outer fee schedules and distinguish assessment, payment and remaining liability."""

import json

import pandas as pd
import streamlit as st

from wealthlab.household.advisory_example import plan
from wealthlab.household.report import encode


def controls(payload, scenario):
    with st.expander("Outer advisory AUM fees and actual cash payment"):
        if not st.checkbox(
            "Assess sourced outer advisory fees",
            value=scenario.advisory_fee_plan is not None,
            key="advisory_enabled",
        ):
            return None
        st.caption(
            "Declare sourced progressive marginal tiers or whole-relationship breakpoint rates "
            "on the complete covered base; breakpoint upper limits are inclusive. "
            "Use actual days/day count or an explicitly source-confirmed fixed annual fraction. "
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
            "Sourced advisory rate methods, periods and coverage (JSON)",
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
        "All simultaneous schedules share one observed snapshot. The declared rate method "
        "applies marginal bands or one whole-relationship breakpoint rate. Actual days remain "
        "exclusive accrual end minus accrual start; a supplied fixed annual fraction replaces "
        "only the variable fee factor, never observation/payment dates or refund rights. "
        "No period fraction or tax deduction is inferred. Reserved cash belongs to the household. "
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
    with st.expander("Sourced fee bases, rate methods, period factors and payment audit"):
        st.json(encode(audit))
