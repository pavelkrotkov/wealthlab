"""Qualified 529 institution payments share the household's cash and tax book."""

import json

import streamlit as st


def controls(payload, scenario):
    with st.expander("Household 529 funding and qualified tuition"):
        enabled = st.checkbox(
            "Project 529 deposits and direct qualified tuition",
            value=bool(payload.get("education_plan")),
        )
        st.caption(
            "Complete calendar years; supplied plan caps and basis; explicit published or "
            "frozen-2026 assumptions. Tuition requests are separate net qualified institution "
            "bills after aid, credits and other vehicles. Exclude those bills from ordinary "
            "education budgets. Confirm institution/enrollment and any room/board limits. "
            "529 assets pay first; available household cash pays the rest at education priority. "
            "Unpaid bills are spending failures. Deposits follow HSA movements and precede IRA "
            "elections/current tax; they can reduce spending cash. NJBEST deductions use actual "
            "funded deposits and completed NJ gross income, not a forecast or cash refund. "
            "Owner reimbursements, nonqualified distributions, K-12, loans, rollovers, gift tax "
            "and full deduction-history recapture require other models."
        )
        if not enabled:
            return None
        return st.text_area(
            "529 plan terms, actual deposits and separate tuition bills (JSON)",
            json.dumps(payload.get("education_plan") or template(scenario), indent=2),
            height=350,
        )


def template(scenario):
    return dict(
        rule_mode="published",
        people=[
            dict(id=p.id, provenance="assumption", household_cash_member=True)
            for p in scenario.members
        ],
        plans=[],
        accounts=[],
        contributions=[],
        tuition=[],
        returns=[],
        complete_context_confirmed=False,
        qualified_net_expenses_separate_from_other_budgets_confirmed=False,
        contributions_belong_to_filing_unit_confirmed=False,
    )


def display(rows):
    if "education_audit" not in rows[-1]:
        return
    st.subheader("Household 529 deposits and tuition funding")
    a, b, c = st.columns(3)
    a.metric("529 deposits funded", total(rows, "education_deposits"))
    b.metric("Tuition paid from 529 assets", total(rows, "education_wrapper_paid"))
    c.metric("Tuition paid from household cash", total(rows, "education_cash_fallback"))
    st.caption(
        "Direct tuition payments leave 529 assets once and count as education spending. "
        "Cash fallback pays only the remaining bill. Optional unfilled deposits are separate "
        "from unpaid tuition; ordinary education budgets remain additional spending. "
        "Annual deductions depend on final NJ income and the selected law assumptions."
    )
    with st.expander("529 actual orders, carried basis and annual qualification"):
        st.json(json.dumps(rows[-1]["education_audit"], default=str))


def total(rows, key):
    return f"${sum(r[key] for r in rows):,.2f}"
