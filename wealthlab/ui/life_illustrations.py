"""Import actual supplied schedules; unknown policy terms stay visible."""

import streamlit as st

from wealthlab.products.life_illustration import run
from wealthlab.products.life_illustration_csv import replace
from wealthlab.products.life_illustration_example import synthetic
from wealthlab.products.life_illustration_inputs import LifeStudy
from wealthlab.ui.life_illustration_results import display
from wealthlab.ui.uploads import clear, invalid, read, source

NAMESPACE = "life_illustration"


def show():
    st.subheader("Whole-life supplied illustrations")
    st.warning(
        "Supplied illustration audit. Contract tax, MEC, lapse, automatic loan interest and "
        "actual household premium funding are not calculated on this page. Enter guaranteed, "
        "current and stressed values independently; missing terms remain unknown."
    )
    st.caption(
        "Each value is after all cash flows on its date. Enter gross policy values before "
        "outstanding loan debt, and actual external cash only. Embedded fees and retained "
        "dividends already affect values. Stopping premiums needs a separate supplied path; "
        "it does not automatically create a paid-up policy. Retirement-date premiums and "
        "an editable protection need expose obligations separately from investment returns."
    )
    uploaded = st.file_uploader("Load whole-life illustration JSON", type="json")
    if source(uploaded, synthetic().model_dump_json(indent=2), NAMESPACE) is None:
        return
    schedule_import()
    with st.form(NAMESPACE):
        edited = st.text_area(
            "Policy metadata, dated cash flows and supplied values (JSON)",
            key=f"{NAMESPACE}_editor",
            height=400,
        )
        submitted = st.form_submit_button("Audit supplied illustrations", type="primary")
    if submitted:
        calculate(edited)
    if f"{NAMESPACE}_result" in st.session_state:
        display(st.session_state[f"{NAMESPACE}_result"])


def schedule_import():
    with st.expander("Replace schedules from CSV"):
        st.caption(
            "Use the exported CSV header. Rows replace all flows or all values for each "
            "named illustration/type present; other schedules stay unchanged. Blank values "
            "stay unknown. Reconfirm correspondence in the JSON only after checking that "
            "imported values match the selected funding path."
        )
        uploaded = st.file_uploader("Import policy schedules CSV", type="csv")
        if st.button("Replace named policy schedules", disabled=uploaded is None):
            try:
                study = LifeStudy.model_validate_json(st.session_state[f"{NAMESPACE}_editor"])
                revised = replace(read(uploaded), study)
                clear(NAMESPACE)
                st.session_state[f"{NAMESPACE}_editor"] = revised.model_dump_json(indent=2)
            except (ValueError, TypeError) as error:
                invalid(error, NAMESPACE)


def calculate(edited):
    try:
        study = LifeStudy.model_validate_json(edited)
        st.session_state.update(life_illustration_result=run(study), life_illustration_input=edited)
    except (ValueError, TypeError) as error:
        invalid(error, NAMESPACE)
