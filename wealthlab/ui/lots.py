"""A lot-accounting workbench with inspectable inputs and exportable calculation details."""

import streamlit as st

from wealthlab.portfolio.example import synthetic
from wealthlab.portfolio.fee_example import synthetic as fee_example
from wealthlab.portfolio.harvest_example import synthetic as harvest_example
from wealthlab.ui.lot_inputs import edit, read
from wealthlab.ui.lot_results import results


def show():
    st.header("Tax lots and transactions")
    st.warning(
        "Gross lot accounting by default; optional federal wash tracking is available. "
        "Dated sale policies use explicit price snapshots; NJ recognition is an explicit "
        "scenario assumption. Household cash-tax funding remains under construction. "
        "Matched harvesting tax differences are conditional annual liabilities, not cash payments. "
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
    examples = {
        "Basic lot accounting": synthetic,
        "Harvesting comparison": harvest_example,
        "Harvesting with manager fees": fee_example,
    }
    example = st.selectbox("Synthetic example", list(examples))
    uploaded = st.file_uploader("Load lot case JSON", type="json")
    try:
        demo = examples[example]()
        raw = read(uploaded) if uploaded else demo.model_dump_json(indent=2)
        edit(raw)
        if "lot_result" in st.session_state:
            results(st.session_state["lot_result"])
    except (ValueError, TypeError) as exc:
        st.error(str(exc))
