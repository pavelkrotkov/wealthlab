"""Fixed IRA schedules expose provisional in-year taxes next to their household results."""

import json

import streamlit as st

from wealthlab.retirement.ira_household_example import template


def controls(payload, scenario):
    with st.expander("Household IRA withdrawals and conversions"):
        enabled = st.checkbox(
            "Fund household cash with fixed IRA schedules",
            value=payload.get("ira_plan") is not None,
        )
        st.caption(
            "Ordinary USD traditional/Roth IRAs, complete calendar years and fixed dated orders "
            "only. "
            "Confirm complete owner pools, basis and Roth histories; zero defaults are "
            "assumptions. "
            "Conversions move assets without producing spending cash. Returns are supplied dated "
            "events. "
            "Annual basis/tax reconciliation enters December: in-year tax and net-wealth figures "
            "omit "
            "unfinalized IRA tax. Enter estimated payments separately; this is not a safe-harbor "
            "check. "
            "Confirmed optional annual contribution contexts now use actual household cash. "
            "Deposits settle after monthly IRA movements, before current tax/spending; "
            "only funded deposits add basis. Completed supported W-2/MAGI checks run after "
            "December tax funding. Social Security deduction worksheets and passive-loss "
            "refiguring still block that combined profile. Workplace/inherited withdrawals, "
            "IRA withholding and automatic withdrawal selection remain unsupported. "
            "RMD targets use the existing December "
            "policy."
        )
        if not enabled:
            return None
        plan = payload.get("ira_plan") or template(scenario).model_dump(mode="json")
        return st.text_area(
            "IRA pools, products, fixed orders and net returns (JSON)",
            json.dumps(plan, indent=2),
            height=350,
        )


def display(rows):
    if "ira_withdrawal_cash" not in rows[-1]:
        return
    st.subheader("Household IRA funding and annual reconciliation")
    st.caption(
        "Fixed withdrawals fund cash once; conversions remain in the same owner's Roth IRA. "
        "Until December, tax and net-wealth figures exclude unfinalized IRA tax. "
        "Unfilled optional orders do not become cash; resulting spending/tax gaps remain failures. "
        "A missed RMD target is shown separately; its potential excise tax is not computed."
    )
    cash, conversion, unfilled = st.columns(3)
    cash.metric("IRA withdrawal cash", f"${sum(r['ira_withdrawal_cash'] for r in rows):,.2f}")
    conversion.metric(
        "IRA conversion transfers", f"${sum(r['ira_conversion_value'] for r in rows):,.2f}"
    )
    unfilled.metric(
        "Unfilled IRA requests", f"${sum(r['ira_unfilled_requests'] for r in rows):,.2f}"
    )
    with st.expander("IRA annual pools, RMD targets and order audit"):
        st.json([r["ira_annual_reconciliation"] for r in rows if "ira_annual_reconciliation" in r])
