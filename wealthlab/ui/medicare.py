"""Medicare premiums expose lookback income, future assumptions and dated funding failures.

A zero ending arrears balance does not imply spending safety. The display keeps
the original missed payment amount visible even after later receipts cure it.
"""

import json

import streamlit as st

from wealthlab.retirement.medicare import run
from wealthlab.retirement.medicare_example import synthetic
from wealthlab.retirement.medicare_inputs import MedicareCase
from wealthlab.ui.uploads import invalid, source


def show():
    st.header("Medicare and IRMAA cash projections")
    st.caption(
        "Full Part B and Part D income surcharges use published 2026 schedules. Later years "
        "require explicit frozen or indexed-2026 assumptions; these are not published future "
        "law. Supplied Part A, drug-plan and other health costs are in 2026 dollars."
    )
    st.info(
        "Enrollment and standard Part B applicability require confirmation. Turning 65 or "
        "retiring does not automatically enroll a person. MAGI equals AGI plus tax-exempt "
        "interest from the return two years earlier; joint income is not split between "
        "spouses. A three-year fallback requires confirmation and missing two-year history. "
        "A recent-income redetermination is a conditional SSA decision, not automatic relief. "
        "Separate-filer lived-apart treatment also requires the individual SSA attestation."
    )
    st.caption(
        "Coverage uses whole months and an exclusive end date. Premiums accrue on the first "
        "of the month as a planning convention. Available cash pays oldest bills first; "
        "later receipts can cure arrears, with actual modeled payment dates shown. Supplied "
        "coverage continues during funding failure; the model does not determine cancellation. "
        "Hold-harmless, immunosuppressive-only Part B, late penalties, subsidies, Advantage "
        "rebates, actual billing dates, Social Security withholding and HSA/household tax "
        "integration remain unfinished. Other health costs are supplied estimates."
    )
    uploaded = st.file_uploader("Load Medicare case JSON", type="json")
    raw = source(uploaded, synthetic().model_dump_json(indent=2), "medicare")
    if raw is None:
        return
    with st.form("medicare_case"):
        edited = st.text_area(
            "Coverage, income history and cash receipts (JSON)", key="medicare_editor", height=400
        )
        submitted = st.form_submit_button("Project Medicare costs", type="primary")
    if submitted:
        try:
            case = MedicareCase.model_validate_json(edited or "")
            st.session_state["medicare_result"] = run(case)
            st.session_state["medicare_input"] = case.model_dump_json(indent=2)
        except ValueError as error:
            invalid(error, "medicare")
    if "medicare_result" in st.session_state:
        display(st.session_state["medicare_result"])


def display(result):
    st.metric("Cash after modeled premium payments", f"${result['cash']:,.2f}")
    st.metric("Outstanding health costs", f"${result['outstanding']:,.2f}")
    missed = sum(row["unfunded_at_due"] for row in result["monthly"])
    st.metric("Health costs unfunded when due", f"${missed:,.2f}")
    st.caption("Later payments can clear arrears; they do not erase an earlier funding failure.")
    st.subheader("Monthly coverage costs and income lookback")
    st.dataframe(result["monthly"], hide_index=True, width="stretch")
    st.subheader("Dated payments, including cured arrears")
    st.dataframe(result["payments"], hide_index=True, width="stretch")
    with st.expander("Rules, assumptions and totals", expanded=True):
        st.json(json.dumps(result, default=str))
    st.download_button(
        "Export Medicare inputs",
        st.session_state["medicare_input"],
        "medicare-case.json",
        "application/json",
    )
    st.download_button(
        "Export Medicare result",
        json.dumps(result, default=str, indent=2),
        "medicare-result.json",
        "application/json",
    )
