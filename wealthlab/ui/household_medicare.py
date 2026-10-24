"""Direct-bill premiums expose lookback income and cash liabilities beside household results."""

import json

import streamlit as st

from wealthlab.retirement.medicare_household_template import template


def controls(payload, scenario):
    with st.expander("Medicare healthcare and benefit premiums"):
        enabled = st.checkbox(
            "Project Medicare bills from completed household tax history",
            value=payload.get("medicare_plan") is not None,
        )
        st.caption(
            "Use complete calendar years. Choose direct_bill_only without benefit checks, or "
            "ssa_current_premiums with generated household claims. The SSA profile requires "
            "one combined payment per recipient, no Part A premium, standard full Part B, "
            "no third-party payer and no prior credits/arrears or other benefit deductions, "
            "and a sufficient active benefit record. This household profile requires all members "
            "to survive; survivor collection needs the later household mortality layer. "
            "Low-benefit Part B "
            "collection remains unsupported. Part D plan costs stay cash-paid; IRMAA-D is "
            "withheld when supported and fully available. Supply prior return history; later "
            "MAGI comes from completed household AGI plus exempt interest two years earlier. "
            "Zero starter history and enrollment are unconfirmed. Future premiums are "
            "conditional. Remove these costs from other expenses. Unpaid bills remain "
            "liabilities. HSA reimbursement, medical deductions "
            "and actual billing are not inferred."
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
    benefit_summary(rows)
    with st.expander("Medicare bills, dated payments and income lookback audit"):
        st.json(rows[-1]["medicare_audit"])


def benefit_summary(rows):
    if "social_security_gross_credited" not in rows[-1]:
        return
    gross, net, held = st.columns(3)
    gross.metric(
        "Gross Social Security credited",
        f"${sum(r['social_security_gross_credited'] for r in rows):,.2f}",
    )
    net.metric(
        "Social Security cash received", f"${sum(r['social_security_cash'] for r in rows):,.2f}"
    )
    held.metric(
        "Medicare withheld from benefits",
        f"${sum(r['medicare_benefit_withheld'] for r in rows):,.2f}",
    )
    st.caption(
        "Taxes use gross credited benefits. Healthcare spending includes withheld "
        "and cash-paid premiums once. Part B changes per-record rounding; "
        "Part D IRMAA is collected afterwards."
    )
