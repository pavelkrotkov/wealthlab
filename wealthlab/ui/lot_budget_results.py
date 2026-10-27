"""Quote estimates and actual return totals measure different things and never share cash."""

import streamlit as st


def display(audit):
    budgets = audit.get("budget_audit", [])
    if not budgets:
        return
    st.subheader("Tax-budget estimates and actual return")
    columns = {
        "Policy": "policy",
        "Decision date": "decision_date",
        "Forecast": "forecast_id",
        "Budget": "tax_budget",
        "Estimated lot-tax delta at decision": "estimated_delta_at_decision",
        "Estimate with later trades": "estimate_after_observed_trades",
        "Later estimate within budget": "estimated_budget_met_after_observed_trades",
        "Actual return status": "actual_return_status",
        "Post-horizon wash assumption": "terminal_wash_assumption_used",
        "Actual total tax": "actual_total_liability",
        "Actual net tax paid": "actual_net_cash_tax_paid",
    }
    st.dataframe(
        [{label: row[key] for label, key in columns.items()} for row in budgets], hide_index=True
    )
    st.caption(
        "The budget limits an estimated cumulative linked-lot liability difference under a dated "
        "full-year non-lot forecast and fixed deductions. It is not a guaranteed final tax cap. "
        "Later required funding sales remain permitted and can exceed the estimate. Actual total "
        "tax includes all income; actual net paid cash includes only real payments/refunds. "
        "Partial/provisional returns and post-horizon wash assumptions remain labeled. "
        "Forecasts do not add income, deductions "
        "or cash to actual results."
    )
