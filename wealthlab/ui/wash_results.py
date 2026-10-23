"""Put recognized, deferred, denied and unresolved amounts beside each loss sale."""

import streamlit as st


def display(rows, jurisdiction="federal"):
    prefix = jurisdiction + "_"
    tracked = [row for row in rows if prefix + "wash_disallowed" in row]
    if not tracked:
        return
    st.subheader(
        ("Federal" if jurisdiction == "federal" else "NJ conditional") + " wash-sale adjustments"
    )
    fields = {
        "Before wash": prefix + "gross_gain",
        "Recognized": prefix + "recognized_gain",
        "Deferred": prefix + "wash_deferred",
        "Denied": prefix + "wash_permanent",
        "Pending": prefix + "pending_loss",
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
        "Tax-basis gain/loss before and after modeled wash adjustments, in USD. "
        "Deferred amounts enter replacement basis; denied IRA amounts do not. "
        "Pending losses have an unfinished 30-day window. These amounts are not tax savings."
    )
