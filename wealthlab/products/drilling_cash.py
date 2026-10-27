"""Conserve actual capital, commodity receipts, paid costs and creditor obligations.

Calls transfer capital internally. Unpaid calls are contractual constraints,
not another wealth liability on top of the same underlying creditors.
GP-style supplied recourse uses actual wallet cash and may exceed initial capital.
"""

from decimal import Decimal

from wealthlab.household.calendar import money

ZERO = Decimal(0)
COSTS = ("operating_cost", "manager_fee", "liability_cost", "idc_cost", "tangible_cost")


def operating(ledger, observation, wallet):
    requested = ledger.call_owed + observation.capital_call
    funded = wallet.pay(requested)
    ledger.call_owed = requested - funded
    ledger.cash += funded
    for key in ledger.bases:
        ledger.bases[key] += funded
    revenue = money(observation.production_units * observation.commodity_price)
    royalties = money(revenue * observation.royalty_fraction)
    ledger.cash += revenue - royalties
    for key in COSTS:
        ledger.owed[key] += getattr(observation, key)
    recourse_funded = ZERO
    if ledger.plan.household_recourse_for_modeled_creditors:
        needed = max(ZERO, sum(ledger.owed.values(), ZERO) - ledger.cash)
        recourse_funded = wallet.pay(needed)
        ledger.cash += recourse_funded
        for key in ledger.bases:
            ledger.bases[key] += recourse_funded
    paid = pay_creditors(ledger)
    net = revenue - royalties - sum(paid[k] for k in COSTS[:3])
    row = dict(
        date=observation.date.isoformat(),
        capital_call=observation.capital_call,
        call_funded=funded,
        recourse_funded=recourse_funded,
        call_owed=ledger.call_owed,
        production_receipts=revenue,
        royalties=royalties,
        net_operating_income=net,
        paid_costs=paid,
        distribution=ZERO,
        distribution_unfilled=ZERO,
        exit_cash=ZERO,
        blocked_exit=False,
    )
    ledger.property_value = observation.residual_property_value
    return row


def pay_creditors(ledger):
    paid = {}
    for key in ledger.owed:
        paid[key] = min(ledger.cash, ledger.owed[key])
        ledger.cash -= paid[key]
        ledger.owed[key] -= paid[key]
    return paid


def distribute(ledger, requested, wallet):
    paid = min(ledger.cash, requested)
    if paid > min(ledger.bases.values()):
        raise ValueError(
            "Drilling distributions above supplied basis/at-risk need another adapter."
        )
    ledger.cash -= paid
    for key in ledger.bases:
        ledger.bases[key] -= paid
    wallet.deposit(paid)
    return paid


def net_value(ledger):
    return ledger.cash + ledger.property_value - sum(ledger.owed.values(), ZERO)
