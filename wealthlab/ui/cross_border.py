"""Select an annual credit audit or the actual shared household cash consumer."""

import streamlit as st


def show():
    choice = st.radio(
        "Cross-border workbench",
        ["Dated annual credit", "Household foreign taxes", "NJ residence / move"],
    )
    if choice == "Dated annual credit":
        from wealthlab.ui.foreign_credits import show as display
    elif choice == "Household foreign taxes":
        from wealthlab.ui.foreign_tax_household import show as display
    else:
        from wealthlab.ui.nj_residence import show as display
    display()
