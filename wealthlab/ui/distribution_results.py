"""Show received and qualifying amounts first, with entitlement dates available for inspection."""

import streamlit as st


def display(result):
    rows = result["distributions"]
    if not rows:
        return
    st.subheader("Distributions and receivables")
    st.caption(
        f"Earned but unpaid: USD {result['distribution_receivable']:,.2f}. "
        "Receivables count in marked wealth but cannot fund purchases before payment."
    )
    labels = dict(
        security_id="Security",
        account_id="Account",
        amount="Amount · USD",
        paid="Cash received",
        recognized="Tax date reached",
        qualified="Qualified · USD",
        qualification_pending="Pending · USD",
    )
    st.dataframe(
        [{key: row[key] for key in labels} for row in rows],
        hide_index=True,
        width="stretch",
        column_config=labels,
    )
    st.caption(
        "Qualified amounts require confirmed issuer/risk eligibility and observed common-share "
        "holding days. Pending amounts remain ordinary until the requirement is met. "
        "Retirement-account receipts remain inside the account and are not withdrawals. "
        "Use price-only marks; return-of-capital and special fund-loss rules remain unsupported."
    )
    with st.expander("Distribution dates and assumptions"):
        st.dataframe(rows, hide_index=True, width="stretch")
