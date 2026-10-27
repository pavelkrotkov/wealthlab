"""Cash failure and unresolved creditor risks accompany conditional wealth/tax results."""

import json

import streamlit as st

from wealthlab.products.drilling_reporting import annual_returns


def display(result):
    st.dataframe([dict(policy=key, **value) for key, value in result["outcomes"].items()])
    st.caption(result["scope"])
    for key, rows in result["rows"].items():
        st.write(key)
        st.dataframe(
            [{name: value for name, value in row.items() if visible(name)} for row in rows]
        )
        with st.expander(key + " source terms, cost/basis/limit audit and actual tax returns"):
            st.json(
                json.loads(
                    json.dumps(
                        dict(audit=rows[-1]["drilling_audit"], annual_returns=annual_returns(rows)),
                        default=str,
                    )
                )
            )
    st.download_button(
        "Download drilling comparison",
        json.dumps(result, default=str, indent=2),
        file_name="drilling-comparison.json",
        mime="application/json",
    )


def visible(name):
    if name in {"date", "closing_cash", "funding_shortfall", "funding_failure", "net_wealth"}:
        return True
    return name.startswith("drilling_") and name not in {
        "drilling_audit",
        "drilling_deduction_audit",
        "drilling_paid_costs",
    }
