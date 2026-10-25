"""Show executed policy decisions beside the same actual household ledger."""

import streamlit as st

from wealthlab.ui.lot_rebalance_results import display as rebalances


def display(audit):
    rebalances(audit)
    sales = audit.get("sale_decisions", [])
    harvests = audit.get("harvest_decisions", [])
    if not (sales or harvests):
        return
    st.subheader("Actual sale and harvesting decisions")
    if sales:
        st.dataframe(sales, hide_index=True, width="stretch")
    if harvests:
        st.dataframe(harvests, hide_index=True, width="stretch")
    st.caption(
        "Policies use observed month-end marks and actual available shares/cash. "
        "Concentration targets use gross pre-tax household assets; later tax payments and "
        "spending can change the final weight. Harvest replacements require the stated "
        "eligibility assumption. Recognized losses enter the shared tax return; "
        "unusable carry and estimated savings are not deposited into household cash."
    )
