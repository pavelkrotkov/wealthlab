"""Dollar disposition evidence does not establish units, legal termination or later rights."""

from decimal import Decimal

from wealthlab.employment.compensation_termination_state import observed


def evidence(ledger, wallet, tranche, end):
    state = ledger.states[tranche.id]
    records = [row for row in ledger.log if row["tranche"] == tranche.id]
    account_vested = sum(
        (
            ledger.states[t.id]["vested"]
            for t in ledger.plan.tranches
            if t.account == tranche.account
        ),
        Decimal(0),
    )
    result: dict = dict(
        observed_before=end.isoformat(),
        coverage_end_exclusive=ledger.horizon_end.isoformat(),
        account_balance=wallet.balances[tranche.account],
        account_vested_value=account_vested,
        account_reconciles=wallet.balances[tranche.account] == account_vested,
        dollar_positions_zero=not any((state["vested"], state["unvested"])),
        cash_distributed=sum((row["cash"] for row in records), Decimal(0)),
        forfeited_value=forfeited(records),
        market_value_losses=market_losses(records),
        zeroed_by_market_event_ids=zeroed_by_market(records),
        disposition_events=dispositions(records),
        declared_future_events=future_events(ledger, tranche.id, end),
        quantities_known=False,
        contract_units=None,
        separate_deferred_value=None,
        separate_deferred_rights_known=False,
        deferred_scope="Retained value in vested/unvested; separate deferred rights unmodeled",
        contractual_exit_proven=None,
        future_rights_after_horizon=None,
        pending_tax_obligations=None,
        tax_scope="TaxPlan allocations are separate; inspect original inputs and tax position",
        legal_scope="Native tranche tracks dollar values, not contractual termination or units",
    )

    # Only separate supplied termination facts may refine unknown legal fields.
    # Dollar balances and actual cash/disposition observations remain unchanged.
    result.update(observed(ledger, tranche, end, result["account_reconciles"]))
    return result


def forfeited(records):
    return sum(
        (
            row["before"]["unvested"] - row["after"]["unvested"]
            for row in records
            if row["kind"] == "forfeit"
        ),
        Decimal(0),
    )


def market_losses(records):
    return sum(
        (
            max(Decimal(0), sum(row["before"].values()) - sum(row["after"].values()))
            for row in records
            if row["kind"] == "net_return"
        ),
        Decimal(0),
    )


def zeroed_by_market(records):
    return [
        row["event"]
        for row in records
        if row["kind"] == "net_return"
        and sum(row["before"].values()) > 0
        and not sum(row["after"].values())
    ]


def dispositions(records):
    return [
        dict(
            event=row["event"],
            date=row["date"].isoformat(),
            kind=row["kind"],
            bucket=row["bucket"],
            election=row["election"],
            purpose=row["purpose"],
            requested=row["requested_amount"],
            cash=row["cash"],
            before=dict(row["before"]),
            after=dict(row["after"]),
        )
        for row in records
        if row["kind"] in {"distribution", "forfeit"}
    ]


def future_events(ledger, tranche_id, end):
    return [
        event.model_dump(mode="json")
        for event in ledger.events
        if event.tranche == tranche_id and event.date >= end
    ]


def from_rows(rows):
    if not rows:
        return None
    return {
        item["tranche"]: item.get("exit_evidence") for item in rows[-1].get("employer_tranches", [])
    }
