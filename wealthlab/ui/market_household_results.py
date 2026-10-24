"""Visible funding outcomes retain batch identity, path indices and actual ledger detail."""

import json

import pandas as pd
import streamlit as st

from wealthlab.ui.lot_policy_results import display as policy_results


def display(bundle):
    result = bundle["baseline"]
    totals = result["aggregate"]
    a, b, c = st.columns(3)
    a.metric("Funded paths / supplied horizon", f"{totals['successes']} / {totals['paths']}")
    b.metric("Simulated funding fraction", f"{totals['funding_fraction']:.1%}")
    c.metric("Covers entire target age", "Yes" if totals["horizon_covers_target_age"] else "No")
    interval = totals["monte_carlo_95_wilson"]
    if interval is not None:
        st.caption(
            f"95% Wilson interval for simulated funding: {interval[0]:.1%} to {interval[1]:.1%}. "
            "Sampling uncertainty conditional on this model; "
            "not uncertainty in market or tax assumptions."
        )
    st.caption(
        f"Shared realized batch: {result['batch_id']}; path indices: {result['indices']}. "
        f"Horizon ends {totals['end']}; target is through age {totals['target_age']}. "
        "Cash reserve breaches use actual cash versus the entered reserve target. Net-wealth "
        "drawdown includes spending and external flows. Marked terminal wealth includes "
        "unrealized gains; it is not a fully liquidated after-tax exit value."
    )
    st.caption(
        "Funding success uses the spending policy actually requested. Discretionary "
        "spending reductions are reported separately; cutting spending does not mean "
        "the original uncut lifestyle was funded."
    )
    st.dataframe(pd.DataFrame(result["outcomes"]), hide_index=True, width="stretch")
    index = st.selectbox("Household path detail", result["indices"])
    rows = next(d["rows"] for d in result["details"] if d["path"] == index)
    st.line_chart(
        pd.DataFrame(rows)
        .set_index("date")[["closing_cash", "net_wealth", "real_net_wealth"]]
        .astype(float)
    )
    st.dataframe(
        pd.DataFrame(rows).drop(columns=["annual_tax", "lot_audit"], errors="ignore"),
        hide_index=True,
        width="stretch",
    )
    policy_results(rows[-1].get("lot_audit", {}))
    with st.expander("Actual tax, lot and wrapper ledger"):
        st.json(rows)
    if bundle["comparison"]:
        st.subheader("Paired policy changes on identical paths")
        st.dataframe(bundle["comparison"]["differences"], hide_index=True, width="stretch")
    st.download_button(
        "Export actual household market run",
        json.dumps(bundle, default=str),
        "household-market-run.json",
        "application/json",
    )
