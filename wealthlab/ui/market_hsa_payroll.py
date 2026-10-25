"""Expose actual contribution differences beside tax and cash in paired market policies."""

import json

import streamlit as st

from wealthlab.markets.hsa_payroll_example import personal_policy
from wealthlab.ui.hsa_payroll_results import display as payroll_results


def controls():
    match = False
    if st.session_state.get("market_account_scope") == "HSA payroll and employment":
        match = st.checkbox("Compare matched personal-cash HSA policy", value=True)
        st.caption(
            "The automatic control uses the household you submit and requests the same HSA "
            "deposits on identical market/employment paths. Eligible personal deposits may "
            "fund more after work stops because they do not require wages. Compare actual "
            "funded amounts and cash before interpreting tax/wealth differences. Leave the "
            "optional paired JSON empty when using this control."
        )
    raw = st.text_area(
        "Optional paired household policy (JSON)",
        value="",
        height=120,
        key="market_alternative_" + st.session_state["market_account_scope"],
    )
    st.caption(
        "The alternative accepts household JSON or {household, binding}; both policies "
        "receive the same realized market batch and selected path indices."
    )
    return raw, match


def policy_text(household, raw, match):
    if not match:
        return raw
    if raw.strip():
        raise ValueError("Choose automatic personal HSA control or supplied paired JSON, not both.")
    return json.dumps(personal_policy(household).model_dump(mode="json"))


def display(bundle, rows):
    if "hsa_payroll_contributions" not in rows[-1]:
        return
    payroll_results(rows)
    st.caption(
        "Reported tax liabilities use latest per-year recognized amounts and dated return "
        "revisions; unresolved provisional/partial years are identified in the path table. "
        "Gross payments and cash refunds retain actual dates. A lower current cash payment "
        "can leave tax owed, while a lower assessment can remain an unavailable refund. "
        "Matched requests need not produce matched funded deposits when work stops."
    )
    records = outcome_records(bundle["baseline"], "Salary policy")
    if bundle["comparison"]:
        records += outcome_records(bundle["comparison"]["result"], "Paired control")
    st.dataframe(records, hide_index=True, width="stretch")


def outcome_records(result, policy):
    fields = (
        "hsa_salary_reductions",
        "hsa_salary_elections_unfilled",
        "hsa_personal_deposits",
        "hsa_external_employer_funding",
        "hsa_ending_gross_assets",
        "reported_employee_payroll",
        "reported_tax_liability",
        "net_cash_taxes_paid",
        "ending_nominal_wealth",
        "funded",
        "provisional_tax_years",
        "partial_tax_years",
    )
    return [
        dict(policy=policy, path=row["path"], **{k: row.get(k) for k in fields})
        for row in result["outcomes"]
    ]
