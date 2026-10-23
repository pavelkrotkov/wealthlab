"""Put recognized, deferred, denied and unresolved amounts beside each loss sale."""

import streamlit as st


def display(rows):
    tracked = [row for row in rows if "federal_recognized_gain" in row]
    if not tracked:
        return
    st.subheader("Federal wash-sale adjustments")
    fields = {
        "Before wash": "federal_gross_gain",
        "Recognized": "federal_recognized_gain",
        "Deferred": "federal_wash_deferred",
        "Denied": "federal_wash_permanent",
        "Pending": "federal_pending_loss",
    }
    table = [
        dict(Trade=row["trade_id"], **{label: row[key] for label, key in fields.items()})
        for row in tracked
    ]
    st.dataframe(
        table,
        hide_index=True,
        width="stretch",
        column_config={label: st.column_config.NumberColumn(format="$%.2f") for label in fields},
    )
    st.caption(
        "Federal tax-basis gain/loss before and after modeled wash adjustments, in USD. "
        "Deferred amounts enter replacement basis; denied IRA amounts do not. "
        "Pending losses have an unfinished 30-day window. These amounts are not tax savings."
    )
