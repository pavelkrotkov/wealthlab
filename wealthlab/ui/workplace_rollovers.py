"""Source-to-IRA value is an internal transfer, not a spendable household receipt."""

import streamlit as st


def display(rows):
    audit = rows[-1].get("workplace_rollover_audit", [])
    if not audit:
        return
    st.subheader("Actual direct plan-to-IRA transfers")
    st.metric("Direct plan cash rolled into IRAs", f"${sum(r['funded'] for r in audit):,.2f}")
    st.caption(
        "Confirmed fully vested ordinary pretax401(k) sources with zero federal/NJ basis, "
        "same-owner traditional IRAs and first-day dates only. Source cash withdrawals run "
        "first; unresolved current or prior source-plan RMDs block rollover. Requests use "
        "actual unlocked assets and are not retried. No spending cash, source withholding, "
        "deduction or ordinary contribution room is created. The IRA uses its own withdrawal "
        "age tests; the source plan's age55 exception does not follow the transfer. "
        "Plan allocation/nonzero basis, designated Roth, in-flight/60-day transfers and "
        "actual prior-RMD correction remain separate profiles."
    )
    labels = dict(
        date="Transfer date",
        source="Source plan",
        destination="IRA destination",
        requested="Requested rollover",
        funded="Funded rollover",
        unfilled="Unfilled request",
        blocked_by_liquidity="Source locked",
        source_rmd_unresolved="Unresolved source RMD",
    )
    st.dataframe(
        [{label: r[key] for key, label in labels.items()} for r in audit],
        hide_index=True,
        width="stretch",
    )
