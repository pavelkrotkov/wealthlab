"""Annual filing-unit differences are shown apart from cash and portfolio market value."""

import streamlit as st


def display(rows):
    if not rows:
        return
    st.subheader("Annual tax comparison · conditional liability")
    table = [
        {
            "Year": row["year"],
            "Without lot trades": row["without_lot_trades"]["total_liability"],
            "With lot trades": row["with_lot_trades"]["total_liability"],
            "Change": row["incremental_liability"],
            "Federal carry": row["with_lot_trades"]["federal"]["short_carry"]
            + row["with_lot_trades"]["federal"]["long_carry"],
            "Federal pending": row["pending_losses"]["federal"],
            "NJ pending": row["pending_losses"]["nj"],
        }
        for row in rows
    ]
    st.dataframe(table, hide_index=True, width="stretch")
    st.caption(
        "Negative change means lower modeled annual liability. Each comparison uses the same "
        "other income and entered deductions, with separate capital-loss carry paths. "
        "Pending losses receive no deduction. This is not cash tax funding or spendable wealth; "
        "deduction changes from future tax payments are not inferred."
    )
