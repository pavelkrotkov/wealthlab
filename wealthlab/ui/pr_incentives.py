"""Editable conditional decree/source comparisons with an independent ordinary alternative."""

import json

import streamlit as st

from wealthlab.tax.pr_annual import LIMITATION
from wealthlab.tax.pr_decree_facts import PRComparison
from wealthlab.tax.pr_incentive_examples import legacy_dividends, new_gain
from wealthlab.tax.pr_incentives import evaluate

EXAMPLES = {"Legacy US dividends": legacy_dividends, "2027 rules: post-move stock gain": new_gain}


def show():
    st.header("Puerto Rico conditional incentives and pre-move gains")
    st.warning(LIMITATION)
    st.caption(
        "Original synthetic assumptions. Application dates select the legacy/2027 regime; "
        "a granted, effective, compliant, unrevoked decree is a separate claim. "
        "History claims confirm nonresidence from January 17, 2006 through January 17, 2012. "
        "Post-2026 applications also require six years of nonresidence before moving. "
        "Gains support plain public stock only: no inventory, "
        "business/real-property connections, pass-through interests or mixed losses. "
        "Asset allocations derive source portions independently of the row's initial labels. "
        "Federal tax-home FMV and local residence FMV/basis remain separate. "
        "A tax-only result excludes unknown grant/compliance/property costs."
    )
    selected = st.selectbox(
        "Synthetic incentive example", list(EXAMPLES), key="pr_incentive_example"
    )
    key = f"pr_incentive_{selected}"
    case = st.session_state.setdefault(key, EXAMPLES[selected]())
    with st.form("pr_incentive_form"):
        text = st.text_area(
            "Dated incentive configuration (JSON)",
            case.model_dump_json(indent=2),
            height=540,
            key=f"{key}_config",
        )
        submitted = st.form_submit_button(
            "Compare ordinary and decree alternatives", type="primary"
        )
    try:
        if submitted:
            updated = PRComparison.model_validate_json(text)
            result = evaluate(updated)
            st.session_state.update({key: updated, f"{key}_result": result})
        if f"{key}_result" in st.session_state:
            display(st.session_state[f"{key}_result"])
    except (ValueError, OSError) as error:
        st.error(str(error))


def display(result):
    for reason in [*result["reasons"], *result["qualification"]["reasons"]]:
        st.warning(reason)
    for label in ["ordinary", "incentive"]:
        candidate = result[label]
        if candidate is None:
            continue
        if candidate["conditional"]:
            st.warning(f"{label.title()} result remains conditional on supplied assumptions.")
        st.metric(
            f"{label.title()}: federal + PR + payroll",
            f"${candidate['federal_pr_payroll_total']:,.2f}",
        )
        st.caption(
            f"Federal income tax ${candidate['federal']['income_tax']:,.2f}; "
            f"PR income tax ${candidate['puerto_rico']['income_tax']:,.2f}"
        )
    serialized = json.dumps(result, default=str, indent=2)
    st.json(json.loads(serialized), expanded=False)
    st.download_button(
        "Download dated incentive/source audit",
        serialized,
        file_name="synthetic-pr-incentive-audit.json",
        mime="application/json",
    )
