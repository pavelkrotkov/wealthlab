"""First scenario workflow; no taxes, market risk or optimization claims yet."""

import streamlit as st
from pydantic import ValidationError

from wealthlab.household.example import synthetic
from wealthlab.household.projection import project
from wealthlab.ui import editor, files, results


def show():
    st.header("Household cash flow")
    st.warning(
        "Cash-flow foundation: income is gross and taxes are not calculated yet. "
        "Non-cash assets have no returns and are not sold to fund spending. "
        "This screen cannot establish after-tax affordability or retirement safety."
    )
    st.caption(
        "Payments use cash accounts in listed order: debts, fees, essential, healthcare, "
        "mortgage, education, discretionary, then contributions. Unpaid debt interest "
        "accrues; fees remain owed; unmet spending is a shortfall. No new borrowing is assumed."
    )
    try:
        files.import_scenario()
        scenario = st.session_state.setdefault("scenario", synthetic())
        updated = editor.editor(scenario)
        if updated is not None:
            rows = project(updated)
            st.session_state.update(scenario=updated, projection=rows)
            scenario = updated
        rows = st.session_state.get("projection")
        if rows is not None:
            results.display(scenario, rows)
            results.comparison(scenario)
        files.save_scenario(scenario)
    except (ValueError, ValidationError, OSError) as error:
        st.error(str(error))
