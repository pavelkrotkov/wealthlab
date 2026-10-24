"""Select a concrete retirement workbench without growing the application's router."""

import streamlit as st

from wealthlab.ui import education, health_education, medicare, retirement, retirement_withdrawals


def show():
    workbenches = {
        "Contributions": retirement,
        "IRA withdrawals": retirement_withdrawals,
        "HSA": health_education,
        "Education": education,
        "Medicare": medicare,
    }
    mode = st.radio(
        "Retirement workbench", list(workbenches), horizontal=True, key="retirement_mode"
    )
    workbenches[mode].show()
