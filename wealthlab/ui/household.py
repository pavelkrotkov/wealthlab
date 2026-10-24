"""Local cash-flow scenarios with optional explicit annual tax assumptions."""

import streamlit as st
from pydantic import ValidationError

from wealthlab.employment.compensation_example import synthetic as compensation_example
from wealthlab.employment.compensation_stress import linked_shock
from wealthlab.employment.example import synthetic as employment_example
from wealthlab.household.example import synthetic
from wealthlab.household.projection import project
from wealthlab.retirement.social_household_example import synthetic as benefit_example
from wealthlab.ui import editor, files, results


def show():
    st.header("Household cash flow")
    st.warning(
        "Enable household tax assumptions to include federal/NJ taxes. "
        "Without a tax plan, income is gross and taxes are omitted. "
        "Market paths remain unfinished; employer returns use supplied dated events. "
        "Only explicitly permitted taxable accounts can be sold, "
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
        if st.button("Load synthetic Social Security household"):
            files.select_scenario(benefit_example())
            st.rerun()
        if st.button("Load synthetic employment household"):
            files.select_scenario(employment_example())
            st.rerun()
        if st.button("Load synthetic employer compensation household"):
            files.select_scenario(compensation_example())
            st.rerun()
        if st.button("Load synthetic linked employment and asset shock"):
            files.select_scenario(linked_shock())
            st.rerun()
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
