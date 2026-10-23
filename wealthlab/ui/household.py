"""Local cash-flow scenarios with optional explicit annual tax assumptions."""

import streamlit as st
from pydantic import ValidationError

from wealthlab.household.example import synthetic
from wealthlab.household.projection import project
from wealthlab.ui import editor, files, results


def show():
    st.header("Household cash flow")
    st.warning(
        "Enable household tax assumptions to include federal/NJ taxes. "
        "Without a tax plan, income is gross and taxes are omitted. "
        "Assets still have no returns. Only explicitly permitted taxable accounts can be sold, "
        "using entered proportional-basis assumptions. "
        "This screen does not yet establish retirement safety."
    )
    st.caption(
        "Payments use cash accounts in listed order: tax withholding/settlement when enabled, "
        "debts, fees, essential, healthcare, "
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
