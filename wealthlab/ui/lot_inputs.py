"""Edit and validate the workbench payload before replacing any displayed result."""

import csv
import io
import json

import streamlit as st

from wealthlab.household.storage import MAX_BYTES
from wealthlab.portfolio.cases import LotCase
from wealthlab.portfolio.engine import run
from wealthlab.ui import harvest_editor, sale_policy_editor


def edit(raw):
    with st.form("lot_case"):
        edited = st.text_area("Accounts, securities, lots and dated trades (JSON)", raw, height=400)
        lots = st.file_uploader("Replace opening lots from CSV", type="csv")
        nj_mode = st.selectbox(
            "NJ wash treatment override",
            ["Use case JSON", "unconfirmed", "federal_rules", "no_wash_assumption"],
            key="nj_wash_override",
        )
        st.caption(
            "Add lot_tax_cases in JSON for annual liability comparisons. Enter other income "
            "and deductions excluding these lot trades; one case per calendar year. "
            "Only the first case supplies opening capital carries."
        )
        decision = sale_policy_editor.inputs()
        harvest = harvest_editor.inputs()
        submitted = st.form_submit_button("Calculate lot accounting", type="primary")
    if submitted:
        payload = json.loads(edited)
        if not isinstance(payload, dict):
            raise ValueError("Lot case JSON must be an object.")
        if nj_mode != "Use case JSON":
            payload["nj_wash_treatment"] = nj_mode
        sale_policy_editor.append(payload, decision)
        harvest_editor.apply(payload, harvest)
        if lots:
            payload["lots"] = list(csv.DictReader(io.StringIO(read(lots))))
        case = LotCase.model_validate(payload)
        st.session_state["lot_result"] = run(case)
        st.session_state["lot_input"] = case.model_dump_json(indent=2)


def read(uploaded):
    raw = uploaded.getvalue()
    if len(raw) > MAX_BYTES:
        raise ValueError("Lot import exceeds the 2 MB limit.")
    return raw.decode("utf-8-sig")
