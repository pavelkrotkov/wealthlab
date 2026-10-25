"""Complete source coverage and dated access are distinct from supplied Roth cost history."""

from wealthlab.retirement.workplace_roth_history import validate_contract
from wealthlab.retirement.workplace_roth_ids import validate_ids


def validate(scenario):
    plan = scenario.workplace_plan
    cash = plan.roth_cash_withdrawals
    if cash is None:
        return
    validate_coverage(cash, plan)
    accounts = {a.id: a for a in scenario.accounts}
    members = {m.id: m for m in scenario.members}
    for contract in cash.contracts.values():
        validate_contract(contract, accounts, members, scenario.start.year)
    by_source = {s: c for c in cash.contracts.values() for s in c.sources}
    validate_orders(cash, by_source, plan, scenario)


def validate_coverage(cash, plan):
    sources = [s for contract in cash.contracts.values() for s in contract.sources]
    classified = {s for s, kind in plan.products.items() if kind == "roth_401k"}
    if len(sources) != len(set(sources)) or set(sources) != classified:
        raise ValueError("Roth contracts must cover each classified designated Roth source once.")


def validate_orders(cash, by_source, plan, scenario):
    from wealthlab.retirement.workplace_withdrawal_validation import validate_order

    validate_ids(cash, plan)
    for order in cash.orders:
        validate_order(order, by_source, scenario)
    for order in plan.orders:
        contract = by_source.get(order.destination)
        if contract is not None and order.date >= contract.separation_date:
            raise ValueError("Employee deferrals cannot reopen a separated Roth source contract.")
