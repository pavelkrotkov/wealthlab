"""Render conditional annual taxes and unexecuted schedules with separate blocked scopes.

An annual total never implies cash settlement; informational overpayments remain
separate from confirmed refund rights and from the original observed payment FX.
"""

import json

import streamlit as st


def display(result):
    for identity, annual in result["assessments"].items():
        display_annual(identity, annual)
    st.subheader("Remaining tax schedules · EUR")
    for item in result["obligations"]:
        st.json(item)
        if item["status"] == "blocked":
            st.error(f"{item['id']}: {' '.join(item['reasons'])}")
    if result["total_liability_eur"] is not None:
        st.metric(
            "Sum of supplied annual assessments · EUR", f"€{result['total_liability_eur']:,.2f}"
        )
    st.caption("Overpayment is a comparison with assessed tax, not a confirmed refund entitlement.")
    st.download_button(
        "Export annual assessments and tax schedules",
        json.dumps(result, indent=2, default=str),
        "synthetic-spain-assessment-plan.json",
        "application/json",
    )


def display_annual(identity, annual):
    """A wealth-only block leaves independently resolved income figures visible."""
    st.subheader(f"{identity} · {annual['person_id']} · {annual['liability_year']}")
    st.json({k: v for k, v in annual.items() if k != "result"})
    for scope in ("income", "wealth"):
        if annual["result"][scope]["status"] == "blocked":
            st.error(" ".join(annual["result"][scope]["reasons"]))
