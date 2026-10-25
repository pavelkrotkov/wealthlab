"""Select a concrete retirement workbench without growing the application's router."""

import streamlit as st

from wealthlab.ui import (
    education,
    health_education,
    hsa_investments,
    medicare,
    owl_reference,
    retirement,
    retirement_withdrawals,
    social_security,
    social_work,
)


def show():
    workbenches = {
        "Contributions": retirement,
        "IRA withdrawals": retirement_withdrawals,
        "HSA": health_education,
        "HSA investments": hsa_investments,
        "Education": education,
        "Medicare": medicare,
        "Social Security": social_security,
        "Social Security with employment": social_work,
        "OWL household reference": owl_reference,
    }
    mode = st.radio(
        "Retirement workbench", list(workbenches), horizontal=True, key="retirement_mode"
    )
    workbenches[mode].show()
