"""A lot-accounting workbench with inspectable inputs and exportable calculation details."""

import csv
import io
import json

import streamlit as st

from wealthlab.household.storage import MAX_BYTES
from wealthlab.portfolio.cases import LotCase
from wealthlab.portfolio.engine import run
from wealthlab.portfolio.example import synthetic
from wealthlab.ui import sale_policy_editor
from wealthlab.ui.lot_results import results


def show():
    st.header("Tax lots and transactions")
    st.warning(
        "Gross lot accounting by default; optional federal wash tracking is available. "
        "Dated sale policies use explicit price snapshots; NJ recognition is an explicit "
        "scenario assumption. Household cash-tax funding remains under construction. "
        "These results do not establish a harvesting benefit or after-tax wealth. "
        "Amounts are USD; short positions, derivatives and currency translation "
        "are not supported here."
    )
    st.caption(
        "Enable federal_wash_tracking in the JSON only after confirming "
        "opening_wash_context_complete: all retained household purchases from the prior 30 days, "
        "adjusted opening bases and no unresolved earlier loss sales. Use one security ID across "
        "accounts; cross-security conversion matching is not yet supported. Economic cost, "
        "when known, is separate from tax basis. Open loss windows remain pending."
    )
    uploaded = st.file_uploader("Load lot case JSON", type="json")
    try:
        raw = read(uploaded) if uploaded else synthetic().model_dump_json(indent=2)
        with st.form("lot_case"):
            edited = st.text_area(
                "Accounts, securities, lots and dated trades (JSON)", raw, height=400
            )
            lots = st.file_uploader("Replace opening lots from CSV", type="csv")
            nj_mode = st.selectbox(
                "NJ wash treatment override",
                ["Use case JSON", "unconfirmed", "federal_rules", "no_wash_assumption"],
            )
            st.caption(
                "Add lot_tax_cases in JSON for annual liability comparisons. Enter other income "
                "and deductions excluding these lot trades; one case per calendar year. "
                "Only the first case supplies opening capital carries."
            )
            decision = sale_policy_editor.inputs()
            submitted = st.form_submit_button("Calculate lot accounting", type="primary")
        if submitted:
            payload = json.loads(edited)
            if not isinstance(payload, dict):
                raise ValueError("Lot case JSON must be an object.")
            if nj_mode != "Use case JSON":
                payload["nj_wash_treatment"] = nj_mode
            sale_policy_editor.append(payload, decision)
            if lots:
                payload["lots"] = list(csv.DictReader(io.StringIO(read(lots))))
            case = LotCase.model_validate(payload)
            st.session_state["lot_result"] = run(case)
            st.session_state["lot_input"] = case.model_dump_json(indent=2)
        if "lot_result" in st.session_state:
            results(st.session_state["lot_result"])
    except (ValueError, TypeError) as exc:
        st.error(str(exc))


def read(uploaded):
    raw = uploaded.getvalue()
    if len(raw) > MAX_BYTES:
        raise ValueError("Lot import exceeds the 2 MB limit.")
    return raw.decode("utf-8-sig")
