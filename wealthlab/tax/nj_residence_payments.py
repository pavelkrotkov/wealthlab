"""Allocate actual positive NJ settlement across its existing dated return identities.

The residence profile does not infer allocation of payer withholding or move
refunds. Supplied annual allocations reconcile exactly; household settlement
pays only each return's positive liability, preserving one wallet and no early
cross-return refund netting. Overpayments need the shared return cash extension.
"""

from decimal import Decimal

ZERO = Decimal(0)


def validate(case, state):
    if case.nj_residence is None:
        return
    paid = case.nj_residence.actual_payments_by_return
    returns = {r["id"]: r for r in state["residence_returns"]}
    if set(paid) - set(returns):
        raise ValueError("NJ payment allocations must name an actual residence return identity.")
    total = case.payments.nj_withheld + case.payments.nj_estimates
    if sum(paid.values(), ZERO) != total:
        raise ValueError("Actual NJ payments must reconcile to their per-return allocations.")
    if any(value > returns[key]["income_tax"] for key, value in paid.items()):
        raise ValueError(
            "NJ move overpayments/refunds need independent return cash reconciliation."
        )
    for key, item in returns.items():
        item["actual_payments"] = paid.get(key, ZERO)
        item["payable"] = item["income_tax"] - paid.get(key, ZERO)


def allocate(case, amount):
    if case.nj_residence is None or not amount:
        return case
    from wealthlab.tax.annual import evaluate

    state = evaluate(case)["new_jersey"]
    paid = dict(case.nj_residence.actual_payments_by_return)
    remaining = amount
    for item in state["residence_returns"]:
        part = min(remaining, max(ZERO, item["income_tax"] - paid.get(item["id"], ZERO)))
        paid[item["id"]] = paid.get(item["id"], ZERO) + part
        remaining -= part
    if remaining:
        raise ValueError("NJ payment exceeds supported positive per-return liabilities.")
    return case.model_copy(
        update=dict(
            nj_residence=case.nj_residence.model_copy(update=dict(actual_payments_by_return=paid))
        )
    )
