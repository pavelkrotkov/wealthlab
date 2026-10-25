"""Read post-execution state without repricing, funding, closing or netting contracts."""

from decimal import Decimal


def evidence(state, observed_at):
    active = [leg.model_dump(mode="json") for leg in state.active.values()]
    lots = [lot.model_dump(mode="json") for lot in state.book.lots.values()]
    unopened = [leg.id for leg in state.case.legs if leg.opened > observed_at]
    cash = state.book.cash[state.account]
    fee_owed = sum(state.book.fee_owed.values(), Decimal(0))
    receivable = sum(state.entitlements.values(), Decimal(0))
    positions_closed = not any((active, lots, unopened))
    debt_clear = not any((state.loan, state.collateral, fee_owed, cash < 0))
    complete = all((positions_closed, debt_clear, not receivable, not state.failures))
    return dict(
        observed_at=observed_at.isoformat(),
        timing="after_actual_execution_and_cash_settlement",
        account_id=state.account,
        open_contracts=active,
        stock_lots=lots,
        unopened_contract_ids=unopened,
        owned_shares=sum((lot.quantity for lot in state.book.lots.values()), Decimal(0)),
        borrowed_shares=Decimal(0),
        stock_borrow_supported=False,
        stock_borrow_scope="validated_native_long_only_book; external_borrow_not_represented",
        external_borrowed_shares=None,
        cash=cash,
        outside_cash=state.reserve,
        settlement_cash_payable=max(Decimal(0), -cash),
        settlement_loan=state.loan,
        collateral=state.collateral,
        book_fees_owed=fee_owed,
        dividend_receivable=receivable,
        dividend_entitlements=entitlements(state),
        modeled_positions_closed=positions_closed,
        modeled_cash_exit_complete=complete,
        execution_failures=list(state.failures),
        execution_succeeded=not state.failures,
        tax_settlement_complete=None,
        scope="Supplied native contracts/long-only lots; tax settlement remains separate",
    )


def entitlements(state):
    return [
        dict(index=index, amount=amount, pay_date=state.case.dividends[index].pay_date.isoformat())
        for index, amount in state.entitlements.items()
    ]


def from_rows(rows):
    if not rows:
        return None
    audit = rows[-1].get("option_mark_audit", [])
    return audit[-1].get("exit_state") if audit else None
