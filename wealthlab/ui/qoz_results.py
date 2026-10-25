"""Keep taxes, actual cash, investor basis and internal entity debt visible together."""

import json

import streamlit as st


def display(result):
    st.caption(
        f"Primary authorities checked {result['source_checked']}; "
        "future income-tax rates remain the supplied annual policy assumptions."
    )
    st.dataframe([dict(policy=name, **outcome) for name, outcome in result["outcomes"].items()])
    st.caption(
        "These are conditional ending-wealth results, not fully liquidated rankings when "
        "NAV or settlement receivables remain. The liquid policy has disclosed leverage, "
        "cost and liquidity differences; the three federal tax policies share one contract."
    )
    for name, rows in result["rows"].items():
        st.write(name)
        st.dataframe(
            [
                {
                    k: v
                    for k, v in row.items()
                    if (k.startswith("qoz_") and k != "qoz_audit")
                    or k
                    in {
                        "date",
                        "closing_cash",
                        "net_wealth",
                        "tax_unfunded",
                        "tax_position",
                        "funding_failure",
                    }
                }
                for row in rows
            ]
        )
        with st.expander(f"{name} source gains, basis, debt and cash audit"):
            st.json(json.dumps(rows[-1]["qoz_audit"], default=str))
    st.download_button(
        "Download complete QOZ comparison",
        json.dumps(result, default=str, indent=2),
        file_name="qoz-comparison.json",
        mime="application/json",
    )
