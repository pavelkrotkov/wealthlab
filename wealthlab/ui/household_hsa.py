"""Cash HSA transfers expose qualified receipt limits and conditional NJ treatment."""

import json

import streamlit as st

from wealthlab.retirement.hsa_household_template import template
from wealthlab.ui.hsa_invested_results import display as invested_metrics
from wealthlab.ui.medical_bills import display as medical_summary


def controls(payload, scenario):
    with st.expander("Household cash HSA, reimbursements and medical bills"):
        enabled = st.checkbox(
            "Project cash HSA contributions and withdrawals",
            value=payload.get("hsa_plan") is not None,
        )
        st.caption(
            "USD HSAs with separate investment/custodian fees; complete calendar years "
            "and confirmed monthly "
            "eligibility. Personal deposits use available cash before IRA elections/current tax. "
            "Historical receipts must already be paid before this projection and unavailable "
            "for another reimbursement or deduction. One shared ledger prevents reuse across "
            "years. Nonqualified cash requires explicit ordinary/noninvestment classification, "
            "NJ taxable fractions and confirmation against duplicate tax inputs. NJ fractions "
            "apply to the entire actual funded withdrawal, independently of federal receipts. "
            "Net medical bills can use direct HSA elections and actual cash fallback; only paid, "
            "undeducted portions can be reimbursed later. Unpaid bills remain liabilities. "
            "Confirm bills are excluded from other budgets, receipts and deductions. "
            "Optional investments share actual cash, dated prices, fees and explicit NJ basis. "
            "Exclude generated investment income from other tax inputs. Linked recipient NJ "
            "fractions must be zero in this profile. Confirm remaining accounts are cash-only "
            "and clear the all-cash confirmation. Corrections remain unsupported. "
            "Salary reduction is not modeled as a personal deposit. "
            "NJ bank treatment is a confirmed scenario assumption: no personal deduction, "
            "current taxable bank interest and employer funding added to NJ wages. Exclude "
            "that same employer amount from other wage inputs. Do not infer state treatment "
            "from federal HSA exemption or general plan marketing."
        )
        if not enabled:
            return None
        plan = payload.get("hsa_plan") or template(scenario)
        return st.text_area(
            "Cash HSA coverage, prior receipts, medical bills and dated orders (JSON)",
            json.dumps(plan, indent=2),
            height=350,
        )


def display(rows):
    if "hsa_personal_contributions" not in rows[-1]:
        return
    st.subheader("Household cash HSA — conditional NJ bank treatment")
    a, b, c = st.columns(3)
    a.metric("Personal HSA deposits", f"${sum(r['hsa_personal_contributions'] for r in rows):,.2f}")
    b.metric(
        "Qualified HSA distributions",
        f"${sum(r['hsa_qualified_reimbursements'] for r in rows):,.2f}",
    )
    c.metric("Unfilled HSA requests", f"${sum(r['hsa_unfilled_requests'] for r in rows):,.2f}")
    distribution_metrics(rows)
    invested_metrics(rows)
    medical_summary(rows)
    st.caption(
        "Reimbursements transfer existing assets to cash; they are not new earnings. "
        "Only funded personal deposits create the federal deduction. Employer funding and "
        "bank interest add assets once. NJ treatment is conditional and kept separate from "
        "federal treatment. Direct provider payments spend assets without creating household cash. "
        "Other healthcare spending remains in the ordinary budget."
    )
    with st.expander("HSA actual cash orders, annual ingredients and shared receipt balance"):
        st.json(json.dumps(rows[-1]["hsa_audit"], default=str))


def scope_note(plan):
    return " Includes conditional NJ cash-HSA tax treatment." if plan else ""


def distribution_metrics(rows):
    a, b, c = st.columns(3)
    a.metric(
        "Nonqualified federal taxable cash",
        f"${sum(r['hsa_nonqualified_taxable'] for r in rows):,.2f}",
    )
    b.metric("HSA federal additional tax", f"${sum(r['hsa_additional_tax'] for r in rows):,.2f}")
    c.metric(
        "Conditional NJ withdrawal income",
        f"${sum(r['hsa_nj_withdrawal_income'] for r in rows):,.2f}",
    )
    st.caption(
        "Federal nonqualified amounts use the explicit ordinary/noninvestment assumption; "
        "age65/disability exceptions affect additional tax, not ordinary income. "
        "NJ fractions are supplied assumptions, not inferred state basis. Only actual funded "
        "cash is recognized. Tax ingredients are not a second deposit or a hypothetical saving."
    )
