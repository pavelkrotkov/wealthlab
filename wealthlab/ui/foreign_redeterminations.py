"""Show real foreign refund cash beside revised original US returns and payment positions."""

import streamlit as st

from wealthlab.tax.foreign_redetermination_example import synthetic_refund
from wealthlab.ui.foreign_tax_household import show as cash_workbench


def show():
    cash_workbench(
        example=synthetic_refund(),
        notice=(
            "Actual later foreign refunds revise the original US paid-tax year and original "
            "carry vintages only with complete confirmed native returns. The foreign liability "
            "year is separate. Receipt-year cash and FX income never move into an earlier year. "
            "Missing source returns, unresolved treatment and provisional facts block the result. "
            "Interest/penalties/costs require dated expense inputs or an explicit zero assumption."
        ),
    )
    if "foreign_tax_household_result" not in st.session_state:
        return
    _, rows = st.session_state["foreign_tax_household_result"]
    st.subheader("Original US returns and actual final payment positions")
    st.json(rows[-1]["foreign_final_source_returns"])
    st.caption(
        "Original payment inputs remain historical facts. Actual net paid includes subsequent "
        "arrears/refunds. Final positions follow all terminal reconciliation; they are not "
        "selected by sorting separate revision histories."
    )
