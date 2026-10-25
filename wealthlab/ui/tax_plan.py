"""Opt in to an editable household tax plan; no automatic tax-free income defaults."""

import json

import streamlit as st

from wealthlab.tax.projection_example import template


def controls(payload: dict, scenario) -> str | None:
    with st.expander("Household tax assumptions"):
        enabled = st.checkbox(
            "Calculate federal and New Jersey taxes", value=payload.get("tax_plan") is not None
        )
        st.caption(
            "The starter assumes every income stream is wages, 20% federal and 6% NJ wage "
            "withholding, no dependents or deductions, and frozen 2025 tax law. "
            "Edit every affected annual case and income rule. Payroll follows modeled liability. "
            "The default year_end setting pays balances in December; refunds arrive next April. "
            "monthly_accrued pays positive accrued balances monthly as a cash stress case. "
            "Sales fund taxes payable on that schedule; future unpaid tax is not cash-reserved. "
            "Dated events can supply withholding with gross_cash, federal_income_withheld and "
            "nj_withheld; cash_received must equal gross minus withheld tax. Only net cash is "
            "deposited, while source tax is credited without a second cash payment. "
            "Dated estimated payments and optional taxable funding accounts are editable below. "
            "Funding uses proportional basis, explicit gain character and allowed/denied losses. "
            "Actual-payments mode adds NJ opening and new cash payments to the federal "
            "state-tax deduction; the entered deduction must exclude those NJ amounts. "
            "Other deductions remain annual assumptions. A state refund with a prior tax "
            "benefit requires an explicit taxable-fraction assumption keyed by its source year. "
            "This is a planning convention, not a filing/payment calendar."
        )
        if not enabled:
            return None
        plan = payload.get("tax_plan") or template(scenario).model_dump(mode="json")
        return st.text_area(
            "Annual tax cases, income rules and dated events (JSON)",
            json.dumps(plan, indent=2),
            height=300,
        )
