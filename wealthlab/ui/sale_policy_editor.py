"""An optional dated decision complements bulk policies in the case JSON editor."""

import json

import streamlit as st

from wealthlab.portfolio.policies import SalePolicy


def inputs():
    with st.expander("Add a sale decision"):
        enabled = st.checkbox("Add this decision when calculating", key="sale_enabled")
        mode = st.selectbox(
            "Decision",
            ["retain", "sell_all", "original_fraction", "target_weight", "tax_budget"],
            key="sale_mode",
        )
        st.caption(
            "Original fraction is a cumulative share-sale target for this account. "
            "Target weight covers all configured accounts and cash, before tax. "
            "Manual trades run first on the same day. Add further dates in sale_policies JSON."
        )
        identity = st.text_input("Decision ID", "ui_sale", key="sale_id")
        when = st.date_input("Decision date", value=None, key="sale_date")
        account = st.text_input("Sale account ID", key="sale_account")
        security = st.text_input("Sale security ID", key="sale_security")
        target = st.number_input("Target fraction", 0.0, 1.0, 0.5, key="sale_fraction")
        budget = st.number_input(
            "Cumulative annual tax budget · USD", 0.0, value=1000.0, key="sale_tax_budget"
        )
        prices = st.text_input(
            "Prices on decision date for every configured security (JSON)",
            "{}",
            key="sale_prices",
            help='Supply all security IDs, e.g. {"stock": 100, "fund": 50}. '
            "Use prices known on the decision date; closing prices may be from a later date.",
        )
        fee = st.number_input("Sale commission · USD", 0.0, value=0.0, key="sale_fee")
        selection = st.selectbox("Lot priority", ["fifo", "hifo"], key="sale_selection")
    return dict(
        tax_budget=budget if mode == "tax_budget" else None,
        enabled=enabled,
        id=identity,
        date=when,
        account_id=account,
        security_id=security,
        mode=mode,
        fraction=target,
        prices=prices,
        commission=fee,
        selection=selection,
    )


def append(payload, values):
    if not values.pop("enabled"):
        return
    if values["mode"] not in {"original_fraction", "target_weight"}:
        values["fraction"] = None
    values["prices"] = json.loads(values["prices"])
    policy = SalePolicy.model_validate(dict(values, provenance="assumption"))
    payload.setdefault("sale_policies", []).append(policy.model_dump(mode="json"))
