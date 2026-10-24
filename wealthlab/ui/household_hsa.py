"""Cash HSA transfers expose qualified receipt limits and conditional NJ treatment."""

import json

import streamlit as st

from wealthlab.retirement.hsa_household_template import template


def controls(payload, scenario):
    with st.expander("Household cash HSA and historical reimbursements"):
        enabled = st.checkbox(
            "Project cash HSA contributions and qualified reimbursements",
            value=payload.get("hsa_plan") is not None,
        )
        st.caption(
            "Cash-only USD HSAs without fees; complete calendar years and confirmed monthly "
            "eligibility. Personal deposits use available cash before IRA elections/current tax. "
            "Historical receipts must already be paid before this projection and unavailable "
            "for another reimbursement or deduction. One shared ledger prevents reuse across "
            "years. Nonqualified withdrawals, new medical bills, HSA investments and corrections "
            "need later adapters. Salary reduction is not modeled as a personal deposit. "
            "NJ bank treatment is a confirmed scenario assumption: no personal deduction, "
            "current taxable bank interest and employer funding added to NJ wages. Exclude "
            "that same employer amount from other wage inputs. Do not infer state treatment "
            "from federal HSA exemption or general plan marketing."
        )
        if not enabled:
            return None
        plan = payload.get("hsa_plan") or template(scenario)
        return st.text_area(
            "Cash HSA coverage, prior paid receipts and dated orders (JSON)",
            json.dumps(plan, indent=2),
            height=350,
        )


def display(rows):
    if "hsa_personal_contributions" not in rows[-1]:
        return
    st.subheader("Household cash HSA — conditional NJ bank treatment")
    a, b, c = st.columns(3)
    a.metric("Personal HSA deposits", f"${sum(r['hsa_personal_contributions'] for r in rows):,.2f}")
    b.metric("Qualified HSA reimbursements", f"${sum(r['hsa_withdrawal_cash'] for r in rows):,.2f}")
    c.metric("Unfilled HSA requests", f"${sum(r['hsa_unfilled_requests'] for r in rows):,.2f}")
    st.caption(
        "Reimbursements transfer existing assets to cash; they are not new earnings. "
        "Only funded personal deposits create the federal deduction. Employer funding and "
        "bank interest add assets once. NJ treatment is conditional and kept separate from "
        "federal treatment. Current healthcare spending remains in the ordinary household budget."
    )
    with st.expander("HSA actual cash orders, annual ingredients and shared receipt balance"):
        st.json(json.dumps(rows[-1]["hsa_audit"], default=str))


def scope_note(plan):
    return " Includes conditional NJ cash-HSA tax treatment." if plan else ""
