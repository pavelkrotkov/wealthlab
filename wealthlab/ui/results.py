"""Nominal/real cash-flow results with limitations placed beside the outputs.

Nested account/tranche audit records stay outside the numeric plotting frame.
Contingent employer marks have their own summary and do not become cash or
ordinary ending wealth merely because they appear in the reproduction details.
"""

import pandas as pd
import streamlit as st

from wealthlab.household.projection import project
from wealthlab.household.report import encode, payload
from wealthlab.household.scenario import Scenario
from wealthlab.household.storage import fingerprint
from wealthlab.ui.compensation_results import display as compensation_summary
from wealthlab.ui.foreign_tax_results import display as foreign_tax_summary
from wealthlab.ui.household_advisory import display as advisory_summary
from wealthlab.ui.household_education import display as education_summary
from wealthlab.ui.household_hsa import display as hsa_summary
from wealthlab.ui.household_hsa import scope_note
from wealthlab.ui.household_ira import display as ira_summary
from wealthlab.ui.household_ira_deposits import display as ira_deposit_summary
from wealthlab.ui.household_life import display as life_summary
from wealthlab.ui.household_lots import display as lot_summary
from wealthlab.ui.household_lots import scope_note as lot_scope_note
from wealthlab.ui.household_medicare import display as medicare_summary
from wealthlab.ui.household_options import display as option_summary
from wealthlab.ui.household_property import display as property_summary
from wealthlab.ui.household_social_work import display as social_work_summary
from wealthlab.ui.household_workplace import display as workplace_summary
from wealthlab.ui.private_fund_household_results import route_household as sleeve_summary
from wealthlab.ui.projected_tax import display as tax_summary

HIDDEN = [
    "property_audit",
    "property_positions",
    "property_closing_events",
    "advisory_fee_assessments",
    "advisory_fee_audit",
    "account_balances",
    "debt_balances",
    "annual_tax",
    "tax_source_receipts",
    "funding_basis",
    "employer_tranches",
    "employer_event_log",
    "ira_annual_reconciliation",
    "ira_contribution_eligibility",
    "ira_contribution_audit",
    "hsa_audit",
    "hsa_investment_accounts",
    "hsa_investment_security_values",
    "education_audit",
    "lot_audit",
    "medicare_audit",
    "sleeve_positions",
    "option_audit",
    "option_mark_audit",
    "option_tax_audit",
    "option_lots",
    "sleeve_audit",
    "sleeve_tax_assumptions",
    "exchange_fund_audit",
    "qoz_audit",
    "drilling_audit",
    "drilling_paid_costs",
    "drilling_deduction_audit",
    "workplace_audit",
    "workplace_market_audit",
    "workplace_withdrawal_audit",
    "workplace_rmd_audit",
    "workplace_rollover_audit",
    "workplace_roth_audit",
    "workplace_roth_contracts",
    "social_security_work_audit",
    "life_policy_values",
    "life_policy_audit",
    "saving_audit",
    "foreign_tax_positions",
    "foreign_tax_cash_records",
    "foreign_tax_credit",
    "foreign_tax_source_identities",
    "foreign_tax_unresolved",
    "foreign_return_revisions",
    "foreign_redetermination_unresolved",
    "foreign_final_source_returns",
]


def display(scenario: Scenario, rows: list[dict]) -> None:
    st.subheader(scenario.name)
    st.caption(
        ("Synthetic inputs" if scenario.synthetic else "User-entered inputs; verify provenance")
        + scope_note(scenario.hsa_plan)
        + lot_scope_note(scenario.lot_plan)
    )
    table = pd.DataFrame(rows).drop(
        columns=HIDDEN,
        errors="ignore",
    )
    numeric = table.drop(columns=["date", "period_end"]).astype(float)
    nominal, real, gap = st.columns(3)
    nominal.metric("Ending net wealth · nominal USD", f"${rows[-1]['net_wealth']:,.2f}")
    real.metric("Ending net wealth · start-date USD", f"${rows[-1]['real_net_wealth']:,.2f}")
    gap.metric("Unfunded obligations / spending", f"${numeric.funding_shortfall.sum():,.2f}")
    st.caption(
        f"Current spending reserve target: ${rows[-1]['reserve_target']:,.2f} nominal USD. "
        "Spending is annualized from the last period; contributions are excluded. "
        "Taxes, when enabled, add a separate year-to-date liability run rate."
    )
    st.line_chart(numeric.set_axis(table.date)[["closing_cash", "net_wealth", "real_net_wealth"]])
    st.dataframe(table, hide_index=True, width="stretch")
    advisory_summary(rows)
    st.download_button(
        "Export projection inputs, full ledger and reproduction details",
        encode(payload(scenario, rows)),
        "wealthlab-projection.json",
        "application/json",
    )
    tax_summary(rows)
    social_work_summary(rows)
    compensation_summary(rows)
    account_summaries(rows)
    with st.expander("Ending accounts, debts and reproduction details"):
        st.caption(
            "All reported account and debt balances are converted to USD at the stated fixed rates."
        )
        st.json(
            encode(
                dict(
                    accounts=rows[-1]["account_balances"],
                    debts=rows[-1]["debt_balances"],
                    funding_basis=rows[-1].get("funding_basis", {}),
                    input_sha256=fingerprint(scenario),
                    schema_version=scenario.schema_version,
                    ytd=scenario.ytd.model_dump(mode="json"),
                    employer_tranches=rows[-1].get("employer_tranches", []),
                    employer_events=rows[-1].get("employer_event_log", []),
                    exchange_fund=rows[-1].get("exchange_fund_audit"),
                    life_policies=rows[-1].get("life_policy_audit"),
                    qoz=rows[-1].get("qoz_audit"),
                    advisory_fees=rows[-1].get("advisory_fee_audit"),
                    property=rows[-1].get("property_audit"),
                    drilling=rows[-1].get("drilling_audit"),
                )
            )
        )


def comparison(scenario: Scenario) -> None:
    if st.button("Keep this scenario as comparison baseline"):
        st.session_state["baseline"] = scenario
    baseline = st.session_state.get("baseline")
    if baseline is None:
        return
    st.caption(f"Comparison baseline: {baseline.name}. Edit and project to compare a clone.")
    if (baseline.start, baseline.end) != (scenario.start, scenario.end):
        st.warning("Align start and end dates before comparing outcomes.")
        return
    before, after = project(baseline)[-1], project(scenario)[-1]
    st.metric(
        "Ending wealth change versus baseline · nominal USD",
        f"${after['net_wealth'] - before['net_wealth']:,.2f}",
    )


def account_summaries(rows):
    property_summary(rows)
    ira_summary(rows)
    ira_deposit_summary(rows)
    hsa_summary(rows)
    education_summary(rows)
    lot_summary(rows)
    medicare_summary(rows)
    workplace_summary(rows)
    sleeve_summary(rows)
    option_summary(rows)
    life_summary(rows)
    foreign_tax_summary(rows)
