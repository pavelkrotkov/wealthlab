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
        "cost and liquidity differences; the three federal tax policies share one contract. "
        "Timely exit matches the named allowed case: same federal election, fund leverage, "
        "fee/carry rates and return observations, changing "
        "only the sale constraint and settlement delay."
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
        show_revisions(rows[-1]["qoz_audit"].get("source_return_revisions", []))
        with st.expander(f"{name} source gains, basis, debt and cash audit"):
            st.json(json.dumps(rows[-1]["qoz_audit"], default=str))
    st.download_button(
        "Download complete QOZ comparison",
        json.dumps(result, default=str, indent=2),
        file_name="qoz-comparison.json",
        mime="application/json",
    )


def show_revisions(revisions):
    if revisions:
        st.caption(
            "Prior cash rows remain historical. These dated source-year corrections "
            "change remaining tax/refund positions; no instant refund funds a call."
        )
        st.dataframe(
            [
                dict(
                    source_year=r["year"],
                    observed=r["observed"],
                    original_liability=r["old_result"]["total_liability"],
                    revised_liability=r["final_result"]["total_liability"],
                    remaining_refund=r["refund_scheduled"]["cash"],
                    refund_date=r["refund_scheduled"]["date"],
                )
                for r in revisions
            ]
        )
