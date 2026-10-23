"""A lot-accounting workbench with inspectable inputs and exportable calculation details."""

import csv
import io
import json

import streamlit as st

from wealthlab.household.storage import MAX_BYTES
from wealthlab.portfolio.cases import LotCase
from wealthlab.portfolio.engine import run
from wealthlab.portfolio.example import synthetic


def show():
    st.header("Tax lots and transactions")
    st.warning(
        "Gross lot accounting only. Wash-sale adjustments, recognized-loss attribution, "
        "sale policies and household-tax integration are under construction. "
        "These results do not establish a harvesting benefit or after-tax wealth. "
        "Amounts are USD; short positions, derivatives and currency translation "
        "are not supported here."
    )
    uploaded = st.file_uploader("Load lot case JSON", type="json")
    try:
        raw = read(uploaded) if uploaded else synthetic().model_dump_json(indent=2)
        with st.form("lot_case"):
            edited = st.text_area(
                "Accounts, securities, lots and dated trades (JSON)", raw, height=400
            )
            lots = st.file_uploader("Replace opening lots from CSV", type="csv")
            submitted = st.form_submit_button("Calculate lot accounting", type="primary")
        if submitted:
            payload = json.loads(edited)
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


def results(result):
    st.metric("Gross marked wealth · USD", f"${result['gross_wealth']:,.2f}")
    st.caption(result["scope"])
    st.subheader("Gross realized gains by disposed lot")
    st.dataframe(result["disposals"], hide_index=True, width="stretch")
    st.subheader("Original shares sold and ending concentration")
    st.dataframe(result["concentration"]["securities"], hide_index=True, width="stretch")
    st.caption(result["concentration"]["meaning"])
    st.subheader("Remaining lots")
    st.dataframe(result["lots"], hide_index=True, width="stretch")
    st.json(
        {
            key: value
            for key, value in result.items()
            if key not in {"lots", "disposals", "concentration"}
        }
    )
    st.download_button(
        "Export lot inputs", st.session_state["lot_input"], "lot-case.json", "application/json"
    )
    st.download_button(
        "Export lot results",
        json.dumps(result, default=str, indent=2),
        "lot-results.json",
        "application/json",
    )
