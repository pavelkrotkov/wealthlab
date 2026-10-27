"""Acquire new option books from existing household cash, using native trades.

An opening allocation moves capital once. The native option book then purchases
shares, capitalizes acquisition costs, opens contracts and pays actual fees.
Existing holdings are never resized or supplied with a new acquisition basis.
"""

from decimal import Decimal

from wealthlab.optimization.product_example import account as base_account
from wealthlab.products.option_allocation import required_capital, scale_new_plan


def selected(choices):
    offered = [choice.option_units for choice in choices if choice.option_units is not None]
    if len(offered) > 1:
        raise ValueError("Only one dimension can control the option allocation.")
    return offered[0] if offered else 0


def apply(data, binding, opportunity, count):
    if not count:
        return
    if opportunity is None:
        raise ValueError("An option allocation requires a supplied opportunity.")
    if not opportunity.minimum_units <= count <= opportunity.maximum_units:
        raise ValueError("Option units must remain within the supplied bounds.")
    plan = scale_new_plan(
        opportunity.unit,
        count,
        per_unit_fees_confirmed=opportunity.per_unit_absolute_fees_confirmed,
    )
    source = next(a for a in data["accounts"] if a["id"] == opportunity.cash_account)
    available, cost = Decimal(source["balance"]), required_capital(plan)
    if cost > available:
        raise ValueError("Opening option purchases cannot exceed available source cash.")
    insert(data, binding, opportunity, plan)
    source["balance"] = str(available - cost)


def insert(data, binding, opportunity, plan):
    if data["option_plan"] is not None or binding["options"] is not None:
        raise ValueError("A new option allocation cannot replace an existing option book.")
    if plan.account_id in {a["id"] for a in data["accounts"]}:
        raise ValueError("New option purchases require a distinct destination account.")
    data["accounts"].append(account(opportunity, required_capital(plan)))
    data["option_plan"] = plan.model_dump(mode="json")
    binding["options"] = opportunity.binding.model_dump(mode="json")


def account(opportunity, amount):
    return dict(
        base_account(opportunity.unit.account_id, "taxable"),
        owner=opportunity.owner,
        provenance=opportunity.provenance,
        balance=str(amount),
    )
