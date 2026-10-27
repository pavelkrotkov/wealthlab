"""One assessment book joins existing receipts, saving and ordinary fee payment.

Requested historical snapshots are captured only when native execution reaches
that cutoff. The cache never reads a later supplied mark merely because the
complete scenario contains it. Fee reservations encumber cash without moving it.
"""

from contextlib import nullcontext
from datetime import timedelta
from decimal import Decimal

from wealthlab.household import flows
from wealthlab.household.advisory_ledger import Ledger
from wealthlab.household.advisory_snapshot_values import hsa_debts, opening_life

ZERO = Decimal(0)


def attach(books, scenario):
    if scenario.advisory_fee_plan is not None:
        ledger = Ledger(scenario, lambda: {k: v for b in books for k, v in b.summary.items()})
        books.append(ledger)
        return ledger
    return None


def current(products):
    return getattr(products, "advisory", None)


def prepare(products, wallet, start, end, previous, taxes):
    ledger = current(products)
    if ledger is not None:
        ledger.begin(previous, flows.fee_due(ledger.scenario, start, end))
        if taxes is None:
            ledger.after_receipts(wallet, start, end)


def current_due(products):
    ledger = current(products)
    return ledger.current_due if ledger else ZERO


def optional_reservation(products, wallet):
    ledger = current(products)
    return wallet.reserving(ledger.reserve_amount) if ledger else nullcontext()


def pay(scenario, wallet, start, end, previous, products):
    result = flows.fees(scenario, wallet, start, end, previous, current_due(products))
    ledger = current(products)
    if ledger is not None:
        result.update(ledger.settle(result, end - timedelta(days=1)))
    return result


def observe(products, wallet, when, hsa, cutoff):
    ledger = current(products)
    if ledger is not None and (when, cutoff) in ledger.snapshots.requested:
        life = ledger.observations().get("life_policy_values", [])
        if cutoff == "opening" and when == ledger.scenario.start:
            life = opening_life(ledger.scenario)
        ledger.snapshots.capture(cutoff, when, wallet, life, hsa_debts(hsa))
