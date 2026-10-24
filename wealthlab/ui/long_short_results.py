"""Show economic exposures, cash, debt and failures without an inferred tax benefit."""

import json

import pandas as pd
import streamlit as st


def display(result):
    st.subheader("Paired pre-tax economic outcomes")
    summaries = [dict(path=d["path"], **d["summary"]) for d in result["sleeve"]["details"]]
    st.dataframe(pd.DataFrame(summaries), hide_index=True, width="stretch")
    st.caption(
        "Investor wealth includes remaining sleeve equity and outside cash once. Any negative "
        "equity/loan remains owed; liquidation does not cap losses at initial capital. "
        "A margin failure is separate from household spending failure. The supplied monthly "
        "maintenance rule does not certify a broker's intramonth requirements."
    )
    st.dataframe(pd.DataFrame(result["differences"]), hide_index=True, width="stretch")
    index = st.selectbox("Economic path detail", result["sleeve"]["indices"])
    detail = next(d for d in result["sleeve"]["details"] if d["path"] == index)
    rows = pd.DataFrame(detail["rows"]).set_index("date")
    st.line_chart(
        rows[["investor_wealth", "equity", "financing_loan", "outside_cash"]].astype(float)
    )
    st.dataframe(rows, width="stretch")
    with st.expander("Matched reference, assumptions and realized batch"):
        st.json(result)
    st.download_button(
        "Export product economic comparison",
        json.dumps(result, default=str),
        "long-short-economic-run.json",
        "application/json",
    )
