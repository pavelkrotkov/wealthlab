"""Inspect dated IRA cash movements and their independently reconciled tax effects."""

import json

import streamlit as st

from wealthlab.retirement.distribution_example import synthetic
from wealthlab.retirement.distribution_inputs import DistributionCase
from wealthlab.retirement.distributions import run
from wealthlab.ui.uploads import source


def show():
    st.header("IRA withdrawals and conversions")
    st.caption(
        "Ordinary, non-inherited traditional/Roth IRAs only, with complete owner-wide history. "
        "Confirm opening_context_complete: all IRA accounts/history, no prior deferred RMD, "
        "outstanding rollover or current-year regular contribution. "
        "Opening balances are prior December 31 values. Fixed dated schedules draw only actual "
        "available assets; conversions move assets without adding spendable cash. Returns "
        "precede same-day orders and apply to the balance then held."
    )
    st.info(
        "Federal basis uses annual Form 8606-style aggregation; NJ uses separately combined "
        "traditional and Roth owner pools. Final-year values reconcile actual tax recognition "
        "after all cash decisions. They do not enter earlier decisions. Roth qualification "
        "requires the first-contribution clock and age 59½; conversion recapture has its own clock."
    )
    st.caption(
        "An early-penalty exception is an explicit conditional assumption for the entire "
        "withdrawal, not a validated eligibility decision. Disability, death, first-home Roth "
        "qualification, mixed qualified/nonqualified NJ Roth withdrawals, workplace/inherited "
        "accounts, current-year regular contributions and outstanding rollovers are unfinished. "
        "RMDs target December 31; first-year deferral, arrears and shortfall excise tax "
        "are excluded. "
        "Tax forecasts exclude these modeled flows; tax liability is reported but not cash-funded."
    )
    uploaded = st.file_uploader("Load IRA withdrawal JSON", type="json")
    raw = source(uploaded, synthetic().model_dump_json(indent=2))
    if raw is None:
        return
    if st.session_state.get("withdrawal_source") != raw:
        st.session_state.pop("withdrawal_result", None)
        st.session_state.pop("withdrawal_input", None)
        st.session_state["withdrawal_source"] = raw
    with st.form("ira_withdrawals"):
        edited = st.text_area("IRA history, returns and withdrawal orders (JSON)", raw, height=400)
        submitted = st.form_submit_button("Project IRA withdrawals", type="primary")
    if submitted:
        try:
            case = DistributionCase.model_validate_json(edited or "")
            st.session_state["withdrawal_result"] = run(case)
            st.session_state["withdrawal_input"] = case.model_dump_json(indent=2)
        except ValueError as error:
            st.error(str(error))
    result = st.session_state.get("withdrawal_result")
    if result is not None:
        display(result)


def display(result):
    """Show gross cash separately from the incremental annual tax obligation.

    Reconciliation does not pay that obligation or make it spendable wealth;
    the later household layer must fund it through the ordinary cash ledger.
    """
    st.metric("Cash received before tax payments", f"${result['cash']:,.2f}")
    st.subheader("Dated IRA cash and annual recognition")
    st.dataframe(result["orders"], hide_index=True, width="stretch")
    st.subheader("Remaining owner basis and conversion buckets")
    st.json(json.dumps(result["owners"], default=str))
    st.subheader("Required withdrawal targets")
    st.json(json.dumps(result["rmd"], default=str))
    st.caption("Unmet December targets are visible; shortfall excise tax is not calculated.")
    if result["annual_tax"] is not None:
        annual = result["annual_tax"]
        st.metric("Additional annual tax liability", f"${annual['additional_liability']:,.2f}")
        with st.expander("Matched annual tax details"):
            st.json(json.dumps(annual, default=str))
    else:
        st.info("Add annual_tax_case to calculate matched federal/NJ liabilities.")
    st.download_button(
        "Export IRA withdrawal inputs",
        st.session_state["withdrawal_input"],
        "ira-withdrawals.json",
        "application/json",
    )
    st.download_button(
        "Export IRA withdrawal result",
        json.dumps(result, default=str, indent=2),
        "ira-withdrawal-result.json",
        "application/json",
    )
