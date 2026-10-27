"""Explicit scenario import and private-directory save controls."""

from pathlib import Path

import streamlit as st

from wealthlab.household.storage import loads, save_new


def import_scenario():
    upload = st.file_uploader("Load scenario JSON", type="json")
    if upload is not None and st.button("Load selected scenario"):
        scenario = loads(upload.getvalue())
        select_scenario(scenario)
        st.rerun()


def select_scenario(scenario):
    for key in list(st.session_state):
        if key.startswith(("table_", "csv_", "advisory_")):
            del st.session_state[key]
    st.session_state["scenario"] = scenario
    st.session_state.pop("projection", None)


def save_scenario(scenario):
    with st.expander("Save a private scenario"):
        st.caption(
            "Choose an existing private directory outside the public repository. "
            "Saving is atomic and never overwrites an existing file."
        )
        directory = st.text_input(
            "Private directory", placeholder="Select your private scenario folder"
        )
        filename = st.text_input("New scenario filename", "scenario.json")
        if st.button("Save new file"):
            if not directory:
                raise ValueError("Select a private directory before saving.")
            target = save_new(scenario, Path(directory), filename)
            st.success(f"Saved {target.name} in the selected private directory.")
