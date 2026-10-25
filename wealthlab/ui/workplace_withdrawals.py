"""Actual plan debits, net receipts and additional tax remain distinct."""

import streamlit as st


def display(rows):
    audit = rows[-1].get("workplace_withdrawal_audit", [])
    if not audit:
        return
    st.subheader("Workplace cash withdrawals")
    st.caption(
        "Confirmed eligible nonperiodic cash from fully vested pretax 401(k) balances with "
        "zero federal/NJ basis. First-day orders precede employee deferrals and month-end "
        "returns. Cash is net of payer withholding; eligible remainder uses at least 20% federal, "
        "with separate RMD and entered NJ rates. Account locks and actual balances limit payment. "
        "The age-55 separation exception uses the separation calendar year and does not "
        "apply to IRA withdrawals. RMD years require explicit plan settings. Roth plan "
        "distributions, "
        "rollovers, inherited "
        "plans, nonzero basis, loans, NUA and other special features require later profiles."
    )
    labels = dict(
        id="Order",
        date="Date",
        source="Plan account",
        requested="Requested gross",
        gross="Paid gross",
        rmd_portion="Required portion",
        eligible_remainder="Eligible remainder",
        net_cash="Net cash received",
        unfilled="Unfilled request",
        additional_tax="Early-distribution additional tax",
        blocked_by_liquidity="Locked",
        separation_age55_exception="Age-55 separation exception",
        below_age59_half="Below age 59½",
    )
    st.dataframe(
        [{label: row[key] for key, label in labels.items()} for row in audit],
        hide_index=True,
        width="stretch",
    )
    with st.expander("Workplace withdrawal tax and cash audit"):
        st.json(audit)
