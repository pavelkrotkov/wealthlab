"""Editable annual Puerto Rico source, residence and credit assumptions."""

import json

import streamlit as st

from wealthlab.tax.pr_annual import LIMITATION, evaluate
from wealthlab.tax.pr_examples import synthetic
from wealthlab.tax.pr_facts import PRCase


def show():
    st.header("Puerto Rico annual tax comparison")
    st.warning(LIMITATION)
    st.caption(
        "Original synthetic inputs. Edit source rows, dated local residence and federal claims "
        "independently. Confirmed means a supplied reviewed fact, not a legal finding by this app. "
        "Assumed eligibility keeps results conditional. Payroll remains on all original wages. "
        "PR deductions must already be allowed and allocated for the residence period. "
        "The US-credit payment input must exclude tax allocated to section 933-excluded income."
    )
    case = st.session_state.setdefault("pr_case", synthetic())
    with st.form("pr_annual_form"):
        text = st.text_area(
            "Annual configuration (JSON)",
            case.model_dump_json(indent=2),
            height=480,
            key="pr_configuration",
        )
        submitted = st.form_submit_button("Compare annual PR taxes", type="primary")
    try:
        if submitted:
            updated = PRCase.model_validate_json(text)
            result = evaluate(updated)
            st.session_state.update(pr_case=updated, pr_result=result)
        if "pr_result" in st.session_state:
            display(st.session_state["pr_result"])
    except (ValueError, OSError) as error:
        st.error(str(error))


def display(result):
    for reason in result["reasons"]:
        st.warning(reason)
    candidate = result["candidate"]
    if candidate is not None:
        if candidate["conditional"]:
            st.warning("Conditional comparison: at least one qualifying fact is assumed.")
        st.metric(
            "Annual federal + PR + employee payroll",
            f"${candidate['federal_pr_payroll_total']:,.2f}",
        )
        st.metric(
            "Federal + payroll mainland comparator",
            f"${candidate['comparable_mainland_federal_payroll']:,.2f}",
        )
        st.metric("PR income tax", f"${candidate['puerto_rico']['income_tax']:,.2f}")
    st.json(json.loads(json.dumps(result, default=str)), expanded=False)
    st.download_button(
        "Download annual source and tax audit",
        json.dumps(result, default=str, indent=2),
        file_name="synthetic-pr-annual-audit.json",
        mime="application/json",
    )
