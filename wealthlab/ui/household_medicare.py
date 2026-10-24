"""Direct-bill premiums expose lookback income and cash liabilities beside household results."""

import json

import streamlit as st

from wealthlab.retirement.medicare_household_template import template


def controls(payload, scenario):
    with st.expander("Direct-billed Medicare healthcare"):
        enabled = st.checkbox(
            "Project Medicare bills from completed household tax history",
            value=payload.get("medicare_plan") is not None,
        )
        st.caption(
            "Use complete calendar years and confirmed direct billing, "
            "without benefit withholding. "
            "Social Security cash/withholding combinations require a later adapter. "
            "Supply pre-projection return history; subsequent MAGI comes from completed household "
            "AGI plus tax-exempt interest two years earlier. Zero starter history, coverage and "
            "premiums are assumptions to replace or confirm. Frozen/indexed future premiums are "
            "conditional. Remove these costs from other expense entries. Payments use the monthly "
            "cash budget; unpaid bills remain liabilities. HSA reimbursement, medical deductions, "
            "actual billing dates and conditional current-income appeals are not inferred."
        )
        if not enabled:
            return None
        plan = payload.get("medicare_plan") or template(scenario)
        return st.text_area(
            "Medicare coverage, prior returns and direct-bill confirmations (JSON)",
            json.dumps(plan, indent=2),
            height=350,
        )


def display(rows):
    if "medicare_due" not in rows[-1]:
        return
    st.subheader("Medicare premiums, lookback and unpaid bills")
    paid, owed, missed = st.columns(3)
    paid.metric("Medicare premiums paid", f"${sum(r['medicare_paid'] for r in rows):,.2f}")
    owed.metric("Unpaid Medicare liability", f"${rows[-1]['medicare_owed']:,.2f}")
    missed.metric(
        "Premium cash unavailable when due", f"${sum(r['medicare_unfunded'] for r in rows):,.2f}"
    )
    st.caption(
        "Premium cash is already included in healthcare spending. Unpaid bills reduce net wealth; "
        "later arrears payments do not erase the original funding failure or count as a new bill. "
        "Coverage continues as supplied during this cash stress. Later IRMAA uses completed "
        "household scenario returns; this is not an SSA determination or actual billing forecast."
    )
    with st.expander("Medicare bills, dated payments and income lookback audit"):
        st.json(rows[-1]["medicare_audit"])
