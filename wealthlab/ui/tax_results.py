"""Show annual liability separately from the balance after entered payments."""

import json

import streamlit as st


def display(case, result: dict) -> None:
    st.metric("Annual federal + NJ liability", f"${result['total_liability']:,.2f}")
    st.metric("Remaining balance after entered payments", f"${result['total_balance']:,.2f}")
    rows = [
        {
            "Tax": "Federal income",
            "Liability": result["federal"]["income_tax"],
            "Remaining balance": result["federal_income_balance"],
        },
        {
            "Tax": "Employee payroll",
            "Liability": result["federal"]["employee_payroll"],
            "Remaining balance": result["payroll_balance"],
        },
        {
            "Tax": "New Jersey income",
            "Liability": result["new_jersey"]["income_tax"],
            "Remaining balance": result["nj_balance"],
        },
    ]
    st.dataframe(rows, hide_index=True, width="stretch")
    st.caption(result["federal"]["policy"])
    st.caption(result["new_jersey"]["policy"])
    with st.expander("Calculation details and carryforwards"):
        st.json(json.loads(json.dumps(result, default=str)))
    st.download_button(
        "Export annual inputs",
        case.model_dump_json(indent=2),
        file_name="annual-tax-case.json",
        mime="application/json",
    )
