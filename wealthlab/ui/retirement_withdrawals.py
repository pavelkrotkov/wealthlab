"""Inspect dated IRA cash movements and their independently reconciled tax effects."""

import json

import streamlit as st

from wealthlab.retirement.distribution_example import synthetic
from wealthlab.retirement.distribution_inputs import DistributionCase
from wealthlab.retirement.distributions import run
from wealthlab.retirement.ira_contribution_example import synthetic as combined
from wealthlab.ui.ira_contribution_results import display as contribution_summary
from wealthlab.ui.uploads import invalid, source


def show():
    st.header("IRA withdrawals and conversions")
    introduction()
    choice = st.selectbox(
        "IRA example", ["Withdrawals and conversions", "Contributions with withdrawals"]
    )
    default = synthetic() if choice == "Withdrawals and conversions" else combined()
    uploaded = st.file_uploader("Load IRA withdrawal JSON", type="json")
    raw = source(uploaded, default.model_dump_json(indent=2), "withdrawal")
    if raw is None:
        return
    with st.form("ira_withdrawals"):
        edited = st.text_area(
            "IRA history, returns and withdrawal orders (JSON)", key="withdrawal_editor", height=400
        )
        submitted = st.form_submit_button("Project IRA withdrawals", type="primary")
    if submitted:
        try:
            case = DistributionCase.model_validate_json(edited or "")
            st.session_state["withdrawal_result"] = run(case)
            st.session_state["withdrawal_input"] = case.model_dump_json(indent=2)
        except ValueError as error:
            invalid(error, "withdrawal")
    result = st.session_state.get("withdrawal_result")
    if result is not None:
        display(result)


def introduction():
    st.caption(
        "Ordinary, non-inherited traditional/Roth IRAs only, with complete owner-wide history. "
        "Confirm opening_context_complete: all IRA accounts/history, no prior deferred RMD, "
        "outstanding rollover or unlisted current-year contribution. "
        "Opening balances are prior December 31 values. Fixed dated schedules draw only actual "
        "available assets; conversions move assets without adding spendable cash. Returns "
        "precede same-day withdrawals; contributions follow them. Receipts precede both. "
        "All current-year contributions and outside cash receipts belong in the optional "
        "contributions plan, sharing the same opening cash/accounts."
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
        "accounts, prior-year deposits made after year end and outstanding rollovers "
        "are unfinished. "
        "RMDs target December 31; first-year deferral, arrears and shortfall excise tax "
        "are excluded. "
        "Tax forecasts exclude modeled IRA flows/deductions. Contribution compensation and MAGI "
        "are confirmed annual assumptions. A tax case checks supported W-2 compensation, "
        "maximum deduction and funded Roth eligibility; Social Security deduction worksheets "
        "and AGI-dependent passive losses require later adapters. Without that tax case, "
        "eligibility remains conditional. Tax liability is reported but not cash-funded."
    )


def display(result):
    """Show gross cash separately from the incremental annual tax obligation.

    Reconciliation does not pay that obligation or make it spendable wealth;
    the later household layer must fund it through the ordinary cash ledger.
    """
    st.metric("Cash remaining before tax payments", f"${result['cash']:,.2f}")
    contribution_summary(result)
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
