"""Lead with matched outcomes; keep gross harvested losses separate from liability savings."""

import streamlit as st


def display(result):
    comparison = result.get("harvest_comparison")
    if comparison:
        st.subheader("Harvesting on vs off")
        rows = [summary("Continue holding", comparison["holding"])]
        if "terminal_exit" in comparison:
            rows.append(summary("Taxable account exit", comparison["terminal_exit"]))
        st.dataframe(
            rows,
            hide_index=True,
            width="stretch",
            column_config={
                key: st.column_config.NumberColumn(format="$%.2f")
                for key in rows[0]
                if key != "View"
            },
        )
        st.caption(comparison["meaning"])
    if result["harvest_decisions"]:
        st.subheader("Harvest decisions")
        st.dataframe(result["harvest_decisions"], hide_index=True, width="stretch")
        st.caption(
            "Only eligible liquid loss lots are sold; replacements use net proceeds. "
            "Future manual household purchases can still cause a wash sale."
        )
    if "terminal_exit" in result:
        st.caption(
            f"Hypothetical exit retains {len(result['terminal_exit']['lots'])} unsold lot(s). "
            "Only the selected taxable accounts are liquidated; "
            "this is not household spendable wealth."
        )
        st.json(result["terminal_exit_assumptions"], expanded=False)


def summary(label, row):
    return {
        "View": label,
        "Marked wealth difference": row["gross_wealth_difference"],
        "Annual tax saving": row["total_tax_saving"],
        "Tax-adjusted difference": row["tax_adjusted_difference"],
        "Extra trading costs": row["extra_transaction_costs"],
    }
