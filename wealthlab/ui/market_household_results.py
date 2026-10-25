"""Visible funding outcomes retain batch identity, path indices and actual ledger detail.

Reported assessments and dated cash payments remain separate. Payroll policy
comparisons display actual funded deposits and unresolved return years.
"""

import json

import pandas as pd
import streamlit as st

from wealthlab.ui.compensation_results import display as employer_results
from wealthlab.ui.household_sleeves import display as sleeve_results
from wealthlab.ui.household_workplace import display as workplace_results
from wealthlab.ui.hsa_invested_results import display as hsa_results
from wealthlab.ui.lot_policy_results import display as policy_results
from wealthlab.ui.market_employer_results import display as employment_results
from wealthlab.ui.market_funding_results import display as funding_results
from wealthlab.ui.market_hsa_payroll import display as payroll_results
from wealthlab.ui.market_medical_results import display as medical_results
from wealthlab.ui.medical_bills import display as bill_results
from wealthlab.ui.results import HIDDEN


def display(bundle):
    result = bundle["baseline"]
    totals = result["aggregate"]
    funding_results(result)
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
    wrapper_scope(result, rows)
    employer_results(rows)
    workplace_results(rows)
    sleeve_results(rows)
    employment_results(result, index)
    medical_results(result, index, rows)
    hsa_scope(result, rows)
    payroll_results(bundle, rows)
    st.line_chart(
        pd.DataFrame(rows)
        .set_index("date")[["closing_cash", "net_wealth", "real_net_wealth"]]
        .astype(float)
    )
    st.dataframe(
        pd.DataFrame(rows).drop(columns=HIDDEN, errors="ignore"),
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


def wrapper_scope(result, rows):
    if not result["binding"].get("wrappers"):
        return
    st.subheader("Wrapper market proxies and concentration coverage")
    st.caption(
        "Each bound account is explicitly a full-account factor proxy. The full monthly "
        "price return plus cash yield applies to its balance at month end and stays invested "
        "inside the wrapper. Earlier dated withdrawals cannot spend that later gain. "
        "Market locks block outgoing withdrawals/conversions; qualified tuition can use "
        "actual household cash fallback. "
        "Account-factor exposure does not identify underlying issuers."
    )
    st.write(
        {
            "Issuer inventory complete": all(
                r["market_issuer_concentration_complete"] for r in rows
            ),
            "Known factor values at horizon": {
                factor: str(value) for factor, value in rows[-1]["market_factor_values"].items()
            },
            "Unmeasured issuer accounts": rows[-1]["market_unmeasured_issuer_accounts"],
        }
    )


def hsa_scope(result, rows):
    if result["binding"].get("hsa_securities"):
        hsa_results(rows)
        if not result["binding"].get("medical_bill_inflation"):
            bill_results(rows)
