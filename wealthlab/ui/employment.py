"""Keep dated work choices editable beside household salary, bonus and retirement inputs."""

import json

import streamlit as st

from wealthlab.employment.example import template


def controls(payload, scenario):
    with st.expander("Employment paths"):
        enabled = st.checkbox(
            "Apply dated pay changes and job loss", value=payload.get("employment_plan") is not None
        )
        st.caption(
            "Choose existing salary/bonus income IDs and their owner. Multipliers apply to "
            "baseline pay, not the previous change. Job loss sets pay to zero; returning to work "
            "sets a new positive multiplier. Daily month fractions follow the household ledger. "
            "Member retirement dates still stop retirement-linked streams, and opening YTD "
            "tax facts do not change. An explicit wage tax plan is required. "
            "Employer grants, vesting, forfeiture, fund returns and distribution elections "
            "are the next layer; no benefit or severance is inferred from losing a job."
        )
        if not enabled:
            return None
        plan = payload.get("employment_plan") or template(scenario)
        return st.text_area(
            "Dated employment choices (JSON)", json.dumps(plan, indent=2), height=300
        )
