"""Keep creditor exposure, conditional taxes and spendable cash separately auditable."""

from wealthlab.products.drilling_cash import ZERO, net_value


def snapshot(ledger, wallet, row):
    value = net_value(ledger)
    wallet.balances[ledger.plan.account_id] = max(ZERO, value)
    liability = max(ZERO, -value) if ledger.plan.household_recourse_for_modeled_creditors else ZERO
    row.update(
        account_value=max(ZERO, value),
        recourse_liability=liability,
        creditor_payables=sum(ledger.owed.values(), ZERO),
        cash=ledger.cash,
        property_value=ledger.property_value,
        federal_basis=ledger.bases["federal"],
        nj_basis=ledger.bases["nj"],
        at_risk=ledger.bases["at_risk"],
        product_failure=bool(
            ledger.call_owed or sum(ledger.owed.values(), ZERO) or row["blocked_exit"]
        ),
    )


def summary(row):
    return {"drilling_" + key: value for key, value in row.items() if key != "date"}


def finish(ledger, rows):
    rows[-1]["drilling_audit"] = dict(
        terms=ledger.plan.model_dump(mode="json"),
        months=ledger.log,
        future_tax_events=[e.model_dump(mode="json") for e in ledger.pending],
        reference_lots=[lot.model_dump(mode="json") for lot in ledger.reference_book.lots.values()],
        reference_disposals=ledger.reference_book.disposals,
        full_tax_optimization_supported=False,
    )


def annual_returns(rows):
    return {row["date"][:4]: row["annual_tax"] for row in rows if "annual_tax" in row}


def total(rows, key):
    return sum(row[key] for row in rows)
