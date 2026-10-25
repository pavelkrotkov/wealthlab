"""Select an annual credit audit or the actual shared household cash consumer."""

import streamlit as st


def show():
    choice = st.radio("Cross-border workbench", ["Dated annual credit", "Household foreign taxes"])
    if choice == "Dated annual credit":
        from wealthlab.ui.foreign_credits import show as display
    else:
        from wealthlab.ui.foreign_tax_household import show as display
    display()
