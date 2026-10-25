"""QOF entity assets, shareholder NAV and actual cash/recognized tax are different observations."""

import pandas as pd
import streamlit as st


def display(result, rows):
    selected = result["binding"].get("qoz")
    if selected is None:
        return
    st.subheader("QOZ shared asset factor and actual fund cash")
    st.caption(
        "The selected asset factor is supplied net of entity-level tax, before native financing, "
        "investor fees, declared dividends and carry. It is not QOF quote/performance history. "
        "Source sales use actual observed stock prices. New calls earn no earlier return. "
        "Factor exposure shows gross entity assets; shareholder NAV and unknown issuer inventory "
        "remain separate. Locks can delay distributions, sales and settlement cash. "
        "Native legal assumptions, tax dates and no-pending-subscription guards still apply."
    )
    columns = [
        "date",
        "qoz_entity_asset_value",
        "qoz_nav",
        "qoz_internal_debt",
        "qoz_call_paid",
        "qoz_dividends",
        "qoz_settlement_cash",
        "qoz_original_gain_included",
    ]
    st.dataframe(pd.DataFrame(rows)[columns], hide_index=True, width="stretch")
    st.write(
        {
            "Return source": selected["return_source_description"],
            "Factor": selected["factor"],
            "Batch": result["batch_id"],
        }
    )
