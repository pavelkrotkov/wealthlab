"""Inspect inside-HSA securities, actual available cash and conditional state income."""

import json

import streamlit as st

from wealthlab.retirement.hsa_investment_example import synthetic
from wealthlab.retirement.hsa_investment_inputs import HSAInvestments
from wealthlab.retirement.hsa_investments import run
from wealthlab.ui.uploads import invalid, source


def show():
    st.header("Inside-HSA investment book")
    st.caption(
        "Dated prices, trades, dividends and confirmed custodian fees share the existing lot "
        "engine. Cash targets sell only permitted liquid shares into the HSA; they do not "
        "withdraw money from it. Ordinary federal investment income is exempt under the "
        "confirmed proper-HSA/no-UBTI profile. NJ securities taxation and separate historical "
        "basis are supplied assumptions. Recipient distributions and household tax payments "
        "are outside this investment-only result."
    )
    uploaded = st.file_uploader("Load invested-HSA book JSON", type="json")
    if source(uploaded, synthetic().model_dump_json(indent=2), "hsa_investment") is None:
        return
    with st.form("hsa_investment"):
        raw = st.text_area(
            "HSA positions, prices and permitted cash targets (JSON)",
            key="hsa_investment_editor",
            height=400,
        )
        submitted = st.form_submit_button("Project inside-HSA investments", type="primary")
    if submitted:
        try:
            plan = HSAInvestments.model_validate_json(raw or "")
            st.session_state["hsa_investment_result"] = run(plan)
            st.session_state["hsa_investment_input"] = plan.model_dump_json(indent=2)
        except ValueError as error:
            invalid(error, "hsa_investment")
    if "hsa_investment_result" in st.session_state:
        display(st.session_state["hsa_investment_result"])


def display(result):
    a, b, c = st.columns(3)
    a.metric("Inside-HSA marked net wealth", f"${result['net_wealth']:,.2f}")
    b.metric("Available HSA cash", f"${sum(result['cash_by_account'].values()):,.2f}")
    c.metric("Unpaid custodian fees", f"${result['fee_summary']['cash_owed']:,.2f}")
    st.caption(
        "Marked assets and unpaid distribution receivables are distinct from cash. Cash "
        "targets retain proceeds inside the HSA; no tax saving is deposited. Fees paid/owed "
        "reduce wealth once. FIFO uses acquisition order, HIFO uses federal/economic basis, "
        "and NJ-HIFO specifically uses separate NJ basis. Conditional gains are ingredients "
        "for an annual return; a loss is not automatically a current tax benefit."
    )
    st.subheader("Conditional NJ income ingredients")
    st.dataframe(
        [dict(year=year, **values) for year, values in result["nj_income_by_year"].items()],
        hide_index=True,
        width="stretch",
    )
    with st.expander("Actual cash targets, executions, holdings and basis"):
        st.json(json.dumps(result, default=str))
    st.download_button(
        "Export invested-HSA inputs",
        st.session_state["hsa_investment_input"],
        "hsa-investment-case.json",
        "application/json",
    )
    st.download_button(
        "Export invested-HSA result",
        json.dumps(result, default=str, indent=2),
        "hsa-investment-result.json",
        "application/json",
    )
