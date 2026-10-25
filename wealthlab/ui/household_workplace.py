"""Employee elections retain gross payroll, taxable wages and locked balances separately."""

import json

import streamlit as st

from wealthlab.retirement.workplace_example import template
from wealthlab.ui.workplace_rmd import display as rmd_display
from wealthlab.ui.workplace_withdrawals import display as withdrawals


def controls(payload, scenario):
    with st.expander("Employee 401(k) payroll elections"):
        enabled = st.checkbox(
            "Project employee pretax and Roth 401(k) contributions",
            value=payload.get("workplace_plan") is not None,
        )
        st.caption(
            "Complete calendar years; one sponsoring employer per owner. Confirm gross wages "
            "before deferrals, all current-year elections and plan permissions. Dated requests "
            "draw that month's own gross wages before tax, debt and spending; available opening "
            "cash cannot replace missing wages. The monthly budget pools receipts and does not "
            "validate payroll dates. Pretax reduces federal/NJ income-tax wages, while employee "
            "payroll still includes it. Roth stays taxable. Limits share actual funded amounts. "
            "Future frozen-rule assumptions are conditional. No employer match, after-tax "
            "non-Roth contributions or rollover are generated. Optional cash_withdrawals "
            "accepts confirmed ordinary eligible pretax 401(k) cash with zero federal/NJ basis, "
            "first-day dates, source withholding and age-55 separation access. Optional rmd "
            "settings "
            "supply complete plan groups, beneficiary tables, December targets and separate "
            "withholding. "
            "Current-employer delays and special distributions remain unfinished."
        )
        if not enabled:
            return None
        plan = payload.get("workplace_plan") or template(scenario)
        return st.text_area(
            "Employee 401(k) eligibility, products and dated elections (JSON)",
            json.dumps(plan, indent=2),
            height=350,
        )


def display(rows):
    if "workplace_contributions" not in rows[-1]:
        return
    withdrawals(rows)
    rmd_display(rows)
    st.subheader("Employee 401(k) cash and wage reconciliation")
    total = sum(r["workplace_contributions"] for r in rows)
    pretax = sum(r["workplace_pretax"] for r in rows)
    a, b, c = st.columns(3)
    a.metric("Employee 401(k) funded", f"${total:,.2f}")
    b.metric("Pretax wage exclusion", f"${pretax:,.2f}")
    c.metric("Roth employee contributions", f"${total - pretax:,.2f}")
    st.caption(
        "These are cash transfers into locked retirement accounts, not spending or returns. "
        "Unfilled optional elections are separate from tax/spending failures. "
        "Income tax withholding uses post-pretax wages; payroll includes elected wages. "
        "No employer match is inferred."
    )
    change = sum(r.get("workplace_market_change", 0) for r in rows)
    st.caption(
        f"Entered or market-bound investment change: ${change:,.2f}. Month-end returns follow "
        "actual funded employee elections and stay inside the plan. Locked plan balances "
        "fund spending only through explicit supported withdrawal orders."
    )
    with st.expander("Employee investment-return audit"):
        st.json(rows[-1].get("workplace_market_audit", []))
    with st.expander("Employee election limits, current-wage blocks and cash audit"):
        st.json(rows[-1]["workplace_audit"])
