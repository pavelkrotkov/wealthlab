"""Annual tax summaries beside monthly household balances and cash payments."""

import json

import streamlit as st


def display(rows: list[dict]) -> None:
    if "annual_tax" not in rows[-1]:
        st.info("Taxes are omitted. Enable household tax assumptions to include them.")
        return
    annual = {row["date"][:4]: row["annual_tax"] for row in rows}
    records = [
        dict(
            year=year,
            federal_income=result["federal"]["income_tax"],
            employee_payroll=result["federal"]["employee_payroll"],
            new_jersey=result["new_jersey"]["income_tax"],
            total_liability=result["total_liability"],
            remaining_balance=result["total_balance"],
        )
        for year, result in annual.items()
    ]
    st.subheader("Taxes on recognized income")
    st.caption(
        "Annual cases include typed opening YTD facts and newly recognized income. "
        "A partial final year is not a complete annual return. Tax owed reduces net wealth; "
        "refunds increase wealth but remain unavailable cash until their receipt month."
    )
    missed = sum(
        row.get("tax_payment_gap", 0) > 0 or row.get("tax_settlement_payment_gap", 0) > 0
        for row in rows
    )
    st.caption(
        f"Months with a missed scheduled tax payment: {missed}. "
        "These timing gaps are separate from outstanding assessed tax."
    )
    st.dataframe(records, hide_index=True, width="stretch")
    with st.expander("Annual tax calculations and policy assumptions"):
        st.json(json.loads(json.dumps(annual, default=str)))
