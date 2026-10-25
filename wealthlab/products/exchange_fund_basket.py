"""Retain exact independent supplied basis totals when distributing a synthetic basket."""

from decimal import ROUND_DOWN, Decimal

from wealthlab.household.calendar import money
from wealthlab.portfolio.models import Lot
from wealthlab.products.exchange_fund_lots import ZERO


def create_basket(book, plan, value, bases, prices, when, direct=False):
    """Cash rounding consumes equal outside basis before the independently supplied allocation.

    The weights describe an assumed legal allocation, not a statutory algorithm.
    A real fund requires partnership asset bases and other supporting facts.
    """
    portions, cash = quantities(plan, value, prices)
    if cash < ZERO:
        raise ValueError("Basket share rounding exceeds available NAV.")
    if cash > min(bases.values()):
        raise ValueError("Basket rounding cash exceeds basis; supply usable prices/weights.")
    remaining = {key: amount - cash for key, amount in bases.items()}
    allocable = dict(remaining)
    for index, (item, quantity) in enumerate(portions):
        assigned = allocate_bases(item, allocable, remaining, index == len(portions) - 1)
        if direct:
            # Direct purchases acquire actual cost basis, independent of partnership allocations.
            cost = money(quantity * prices[item.security.id])
            assigned = dict(federal=cost, nj=cost)
        identity = f"exchange_basket_{index}"
        lot = Lot(
            id=identity,
            provenance="assumption",
            account_id=plan.account_id,
            security_id=item.security.id,
            acquired=when,
            federal_holding_start=when if direct else item.federal_holding_start,
            liquid_after=when,
            quantity=quantity,
            federal_basis=assigned["federal"],
            nj_basis=assigned["nj"],
        )
        book.lots[identity] = lot
        book.origins[identity] = identity
        book.share_order[identity] = (len(book.share_order), ZERO)
        book.allocated_ids.add(identity)
    return cash


def quantities(plan, value, prices):
    portions = []
    invested = ZERO
    for item in plan.basket:
        quantity = (value * item.value_weight / prices[item.security.id]).quantize(
            Decimal(".000001"), rounding=ROUND_DOWN
        )
        if not quantity:
            raise ValueError("Basket allocation is too small for supported share precision.")
        portions.append((item, quantity))
        invested += money(quantity * prices[item.security.id])
    return portions, value - invested


def allocate_bases(item, allocable, remaining, last):
    result = {}
    for key in remaining:
        amount = (
            remaining[key] if last else money(allocable[key] * getattr(item, key + "_basis_weight"))
        )
        result[key] = amount
        remaining[key] -= amount
    return result
