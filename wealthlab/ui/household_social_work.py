"""Separate editable work forecasts from realized payroll; expose claims and debt beside cash."""

import json

import streamlit as st


def controls(payload, scenario):
    with st.expander("Household Social Security work-test policy"):
        enabled = st.checkbox(
            "Include earned-wage work tests", value=scenario.social_work_plan is not None
        )
        st.caption(
            "Requires own-record claims, a tax plan and matching complete calendar years. "
            "Leave actual_monthly_wages null: actual gross federal W2 streams before employee "
            "401(k)/HSA reductions supply them. Edit reported January forecasts and prior grace "
            "history here; unexpected realized wages change later settlement, not earlier checks. "
            "Manual/opening W2, employer allocations and SSA Medicare withholding are blocked. "
            "Refunds/ARF arrears use ordinary receipt-year net benefit taxation with no special "
            "lump-sum election. Dates and recovery fractions remain conditional."
        )
        if not enabled:
            return None
        plan = payload.get("social_work_plan")
        if plan is None:
            st.warning("Load the synthetic earned-wage household or import a complete work policy.")
        return st.text_area(
            "Work-test forecasts and conditional settlement (JSON)",
            json.dumps(plan or {}, indent=2),
            height=300,
        )


def display(rows):
    if "social_security_net_cash" not in rows[-1]:
        return
    st.subheader("Social Security work-test cash and government positions")
    st.caption(
        "Only actual net checks/refunds fund spending and enter federal benefit taxation. "
        "Positive government claims enter net wealth separately; overpayment debt reduces it. "
        "Neither changes liquid cash before settlement. NJ excludes these benefits. "
        "The conditional own-record profile omits special tax elections and earnings-history PIA "
        "recomputation. Frozen2026 work limits and supplied processing assumptions remain visible "
        "in the exported source policy."
    )
    fields = (
        "date",
        "social_security_net_cash",
        "social_security_forecast_withheld",
        "social_security_refund_cash",
        "social_security_recovered_overpayment",
        "social_security_government_receivable",
        "social_security_government_overpayment_debt",
    )
    st.dataframe(
        [{key: row[key] for key in fields} for row in rows], hide_index=True, width="stretch"
    )
    with st.expander("Actual annual earned-wage assessment and reduction credits"):
        st.dataframe(
            rows[-1].get("social_security_work_audit", []), hide_index=True, width="stretch"
        )
