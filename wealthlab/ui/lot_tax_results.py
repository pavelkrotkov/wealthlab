"""Annual filing-unit differences are shown apart from cash and portfolio market value."""

import streamlit as st


def display(rows):
    if not rows:
        return
    st.subheader("Annual tax comparison · conditional liability")
    table = [
        {
            "Year": row["year"],
            "Without portfolio events": row["without_lot_trades"]["total_liability"],
            "With portfolio events": row["with_lot_trades"]["total_liability"],
            "Change": row["incremental_liability"],
            "Federal carry": row["with_lot_trades"]["federal"]["short_carry"]
            + row["with_lot_trades"]["federal"]["long_carry"],
            "Federal pending": row["pending_losses"]["federal"],
            "NJ pending": row["pending_losses"]["nj"],
            "Dividend qualification pending": row["qualification_pending"],
        }
        for row in rows
    ]
    st.dataframe(
        table,
        hide_index=True,
        width="stretch",
        column_config={
            key: st.column_config.NumberColumn(format="$%.2f") for key in table[0] if key != "Year"
        },
    )
    st.caption(
        "Negative change means lower modeled annual liability. Each comparison uses the same "
        "other income and entered deductions, with separate capital-loss carry paths. "
        "Pending losses receive no deduction. This is not cash tax funding or spendable wealth; "
        "deduction changes from future tax payments are not inferred."
    )
    loss_use(rows)


def loss_use(rows):
    st.subheader("Current portfolio loss use · federal allocation convention")
    table = [
        {
            "Year": row["year"],
            "Character": character.replace("_", " "),
            "Recognized loss": amounts["recognized_loss"],
            "Own gains offset": amounts["own_gain_offset"],
            "External net gains offset": amounts["external_gain_offset"],
            "Ordinary income consumed": amounts["ordinary_consumed"],
            "Current loss carried": amounts["ending_carry"],
            "External net gain / loss": amounts["external_net"],
            "Opening carry": amounts["opening_carry"],
        }
        for row in rows
        for character, amounts in row["federal_loss_use"].items()
    ]
    st.dataframe(
        table,
        hide_index=True,
        width="stretch",
        column_config={
            key: st.column_config.NumberColumn(format="$%.2f")
            for key in table[0]
            if key not in ("Year", "Character")
        },
    )
    st.caption(
        "Reporting convention: net within short/long character first, then across characters; "
        "current portfolio losses before external net losses and opening carry; own gains "
        "before external gains. Allocated offsets can displace existing carry and are not "
        "incremental tax savings. Ordinary consumption uses the engine's carry worksheet, "
        "including unused low-income deductions. Carried amounts here trace only this year's "
        "losses; the annual table shows total carry. Prior-year loss origins are not tracked."
    )
