"""Nominal/real cash-flow results with limitations placed beside the outputs.

Nested account/tranche audit records stay outside the numeric plotting frame.
Contingent employer marks have their own summary and do not become cash or
ordinary ending wealth merely because they appear in the reproduction details.
"""

import pandas as pd
import streamlit as st

from wealthlab.household.projection import project
from wealthlab.household.scenario import Scenario
from wealthlab.household.storage import fingerprint
from wealthlab.ui.compensation_results import display as compensation_summary
from wealthlab.ui.household_ira import display as ira_summary
from wealthlab.ui.household_medicare import display as medicare_summary
from wealthlab.ui.projected_tax import display as tax_summary


def display(scenario: Scenario, rows: list[dict]) -> None:
    st.subheader(scenario.name)
    st.caption(
        "Synthetic inputs" if scenario.synthetic else "User-entered inputs; verify provenance"
    )
    table = pd.DataFrame(rows).drop(
        columns=[
            "account_balances",
            "debt_balances",
            "annual_tax",
            "funding_basis",
            "employer_tranches",
            "employer_event_log",
            "ira_annual_reconciliation",
            "medicare_audit",
        ],
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
    tax_summary(rows)
    compensation_summary(rows)
    ira_summary(rows)
    medicare_summary(rows)
    with st.expander("Ending accounts, debts and reproduction details"):
        st.caption(
            "All reported account and debt balances are converted to USD at the stated fixed rates."
        )
        st.json(
            dict(
                accounts=rows[-1]["account_balances"],
                debts=rows[-1]["debt_balances"],
                funding_basis=rows[-1].get("funding_basis", {}),
                input_sha256=fingerprint(scenario),
                schema_version=scenario.schema_version,
                ytd=scenario.ytd.model_dump(mode="json"),
                employer_tranches=rows[-1].get("employer_tranches", []),
                employer_events=rows[-1].get("employer_event_log", []),
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
