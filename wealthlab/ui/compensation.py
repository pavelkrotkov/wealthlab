"""Edit conditional employer tranches beside the household's ordinary income and tax inputs."""

import json

import streamlit as st

from wealthlab.employment.compensation_example import template


def controls(payload, scenario):
    with st.expander("Employer-linked compensation"):
        enabled = st.checkbox(
            "Project employer tranches and cash elections",
            value=payload.get("compensation_plan") is not None,
        )
        st.caption(
            "Vested opening tranche values must reconcile to USD employer accounts. "
            "Unvested values are contingent and cannot fund household spending without "
            "a supplied cash right. Grants, net returns, vesting, forfeiture and distribution "
            "elections have separate dated events and explicit same-day sequence numbers. "
            "A null vest/forfeit amount means the entire remaining value slice. "
            "Tax results use supplied allocations independent of cash elections. Confirm "
            "all income/eligibility assumptions and exclude these new events from other tax "
            "inputs. Distributions have no extra inferred tax; any applicable income must "
            "be included in the supplied allocations. Basis and hypothetical exit tax are "
            "unmodeled. This conditional profile does not classify an actual employer plan."
        )
        if not enabled:
            return None
        plan = payload.get("compensation_plan") or template(scenario)
        if not plan["tranches"]:
            st.info(
                "Add an employer account and its vested opening balance before entering tranches."
            )
        return st.text_area(
            "Tranches, cash rights and allocation-tax assumptions (JSON)",
            json.dumps(plan, indent=2),
            height=350,
        )
