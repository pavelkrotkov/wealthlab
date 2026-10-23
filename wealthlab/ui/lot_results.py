"""Display executed decisions beside the resulting positions and recognized losses."""

import json

import streamlit as st

from wealthlab.ui.harvest_results import display as harvest_results
from wealthlab.ui.lot_tax_results import display as lot_tax_results
from wealthlab.ui.sale_results import display as sale_results
from wealthlab.ui.wash_results import display as wash_results


def results(result):
    st.metric("Gross marked wealth · USD", f"${result['gross_wealth']:,.2f}")
    st.caption(result["scope"])
    harvest_results(result)
    sale_results(result["sale_decisions"])
    st.caption("NJ treatment: " + result["nj_wash_treatment"])
    lot_tax_results(result["annual_tax_comparison"])
    wash_results(result["disposals"])
    wash_results(result["disposals"], "nj")
    st.subheader("Disposed lot details")
    st.dataframe(result["disposals"], hide_index=True, width="stretch")
    st.subheader("Original shares sold and ending concentration")
    st.dataframe(result["concentration"]["securities"], hide_index=True, width="stretch")
    st.caption(result["concentration"]["meaning"])
    st.subheader("Remaining lots")
    st.dataframe(result["lots"], hide_index=True, width="stretch")
    details = {
        key: value
        for key, value in result.items()
        if key not in {"lots", "disposals", "concentration"}
    }
    st.json(json.loads(json.dumps(details, default=str)))
    st.download_button(
        "Export lot inputs", st.session_state["lot_input"], "lot-case.json", "application/json"
    )
    st.download_button(
        "Export lot results",
        json.dumps(result, default=str, indent=2),
        "lot-results.json",
        "application/json",
    )
