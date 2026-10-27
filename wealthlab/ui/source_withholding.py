"""Show payer remittances separately from recipient cash and later refunds."""

import streamlit as st


def display(rows):
    receipts = [receipt for row in rows for receipt in row.get("tax_source_receipts", [])]
    if not receipts:
        return
    st.subheader("Tax withheld at source")
    st.caption(
        "Only net cash reaches the household. Payer-withheld federal/NJ income tax is "
        "credited once, without a second cash withdrawal. Taxable income is entered "
        "separately and may differ from gross cash. Foreign withholding is linked to its "
        "own payment ID in the shared foreign-tax book. Any refund stays unavailable until "
        "its modeled receipt date. These are supplied amounts, not inferred legal rates."
    )
    labels = dict(
        date="Receipt date",
        description="Source",
        gross_cash="Gross cash",
        net_cash="Net cash received",
        federal_income_withheld="Federal tax withheld",
        nj_withheld="NJ tax withheld",
        total_withheld="Total tax withheld",
        foreign_tax_withheld="Foreign tax withheld",
        foreign_payment_id="Foreign payment identity",
    )
    st.dataframe(
        [{labels[key]: value for key, value in row.items()} for row in receipts],
        hide_index=True,
        width="stretch",
    )
