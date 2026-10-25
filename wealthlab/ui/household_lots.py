"""Actual share funding exposes its basis, cash movements and conditional NJ scope."""

import json
from datetime import timedelta
from decimal import Decimal

import streamlit as st

from wealthlab.household.calendar import months
from wealthlab.ui.lot_policy_results import display as policy_results
from wealthlab.ui.lot_return_results import display as return_results
from wealthlab.ui.saving_results import display as saving_results


def controls(payload, scenario):
    with st.expander("Linked taxable lots and household funding"):
        enabled = st.checkbox(
            "Fund household needs from actual lots", value=bool(payload.get("lot_plan"))
        )
        st.caption(
            "Link complete USD taxable accounts with opening shares/bases and one closing mark "
            "per household month. Opening values must equal lots plus brokerage cash. "
            "Manual trades retain dated order; buys use received cash without borrowing. Remaining "
            "brokerage cash sweeps once to household cash before optional wrapper deposits. "
            "Configured FIFO/HIFO funding sales precede other accounts and include "
            "commission, holding periods, separate bases and wash adjustments. Remove the old "
            "proportional seller for every linked account. Confirm complete outside purchases. "
            "NJ recognition is an explicit scenario assumption. This initial profile excludes "
            "issuer distributions, manager fees and wrapper lots. "
            "Dated month-end staged/target sales "
            "and conditional long-only harvesting use actual current marks and household tax. "
            "Targets use gross pre-tax household assets; later tax/spending can change weights. "
            "Account target-weight rebalances run after harvesting using sale proceeds only. "
            "Tax-budget policies require a separate annual-forecast adapter. Unresolved "
            "year-end wash windows default to blocking. Select january_reconcile to observe the "
            "following January and revise the original return. Posted IRA deduction/basis "
            "elections are preserved, even if a larger deduction later becomes permitted. "
            "An unresolved terminal window requires explicit none_for_30_days post-horizon "
            "purchases; it creates no refund cash before receipt. Complete calendar years only."
        )
        if not enabled:
            return None
        return st.text_area(
            "Linked lot book, monthly marks and funding permissions (JSON)",
            json.dumps(payload.get("lot_plan") or template(scenario), indent=2),
            height=350,
        )


def template(scenario):
    return dict(
        case=dict(
            as_of=scenario.start.isoformat(),
            end=(scenario.end - timedelta(days=1)).isoformat(),
            accounts=[],
            securities=[],
            lots=[],
            trades=[],
            closing_prices={},
            federal_wash_tracking=True,
            opening_wash_context_complete=False,
            nj_wash_treatment="unconfirmed",
        ),
        opening_prices={},
        monthly_marks=[
            dict(date=(end - timedelta(days=1)).isoformat(), prices={})
            for _, end in months(scenario.start, scenario.end)
        ],
        year_end_wash_policy="block",
        post_horizon_purchases="unconfirmed",
        funding_sources=[],
        rebalances=[],
        complete_ownership_and_outside_purchases_confirmed=False,
        monthly_settlement_and_cash_sweep_confirmed=False,
        funding_priority="linked_lots_before_other_permitted_accounts",
    )


def display(rows):
    if "lot_audit" not in rows[-1]:
        return
    audit = rows[-1]["lot_audit"]
    st.subheader("Actual linked-lot funding")
    a, b, c = st.columns(3)
    a.metric("Cash from lot funding sales", f"${sum(r['lot_funding_proceeds'] for r in rows):,.2f}")
    b.metric("Linked accounts remaining", f"${sum(audit['account_values'].values()):,.2f}")
    commissions = sum(Decimal(t["commission"]) for t in audit["trades"])
    c.metric("Linked trade commissions", f"${commissions:,.2f}")
    st.caption(
        "Sale proceeds move existing wealth into cash once. Actual recognized gains feed the same "
        "household tax return and payment ledger; no annual tax-saving estimate is deposited. "
        "Remaining assets include unrealized gains. Funding is feasible under the specified "
        "selection order, not globally optimized. Review the explicit NJ wash assumption."
    )
    saving_results(rows)
    return_results(rows, audit)
    policy_results(audit)
    with st.expander("Actual lots, disposals, funding orders and recognized annual gains"):
        st.json(json.dumps(audit, default=str))


def scope_note(plan):
    return " Includes explicit NJ lot-recognition assumptions." if plan else ""
