"""Debit existing opening cash once for a new, explicitly assumed sleeve purchase.

The scenario begins immediately after these hypothetical purchases. Original
noncash holdings and their basis are unchanged, and native books charge entry
costs once. This is not an executed brokerage order or a forecast cash receipt.
"""

from decimal import Decimal

from wealthlab.household.funding import opening_wealth
from wealthlab.optimization.sleeve_scaling import scale


def selections(choices):
    units = {}
    for choice in choices:
        selected = choice.sleeve_units or {}
        if units.keys() & selected.keys():
            raise ValueError("Each sleeve opportunity can be controlled by one dimension only.")
        units.update(selected)
    return units


def apply(data, binding, opportunities, selected):
    offered = {item.id: item for item in opportunities}
    if selected.keys() - offered.keys():
        raise ValueError("Allocation choices must name configured sleeve opportunities.")
    for identity, count in selected.items():
        item = offered[identity]
        if not item.minimum_units <= count <= item.maximum_units:
            raise ValueError("Sleeve purchase units must remain within the supplied bounds.")
        if count:
            purchase(data, binding, item, count)


def purchase(data, binding, opportunity, count):
    sleeve = scale(opportunity.unit, count)
    amount = sleeve.case.opening_equity
    source = next(
        account for account in data["accounts"] if account["id"] == opportunity.cash_account
    )
    available = Decimal(source["balance"])
    if amount > available:
        raise ValueError("Opening sleeve purchases cannot exceed available source cash.")
    source["balance"] = str(available - amount)
    data["accounts"].append(account(opportunity, amount))
    add_sleeve(data, acquired(sleeve, data["start"]))
    binding["sleeves"].append(sleeve.account_id)
    binding["replace_sleeve_observations_confirmed"] = True


def account(opportunity, amount):
    return dict(
        id=opportunity.unit.account_id,
        owner=opportunity.owner,
        currency="USD",
        wrapper="taxable",
        balance=str(amount),
        monthly_fee="0",
        provenance=opportunity.provenance,
    )


def add_sleeve(data, sleeve):
    if data["sleeve_plan"] is None:
        data["sleeve_plan"] = dict(
            sleeves=[],
            other_tax_inputs_exclude_supplied_allocations_confirmed=True,
            actual_household_cash_confirmed=True,
            priority="after_prior_tax_arrears_before_wrapper_deposits_and_current_tax",
        )
    data["sleeve_plan"]["sleeves"].append(sleeve)


def audit(before, after):
    original = {account.id: account for account in before.accounts}
    new = new_capital(original, after)
    return dict(
        timing="hypothetical_opening_cash_purchases_before_monthly_projection",
        original_opening_wealth=opening_wealth(before),
        allocated_opening_wealth=opening_wealth(after),
        new_account_capital=new,
        new_sleeve_capital=sleeve_capital(after, new),
        cash_debits={
            a.id: original[a.id].balance - a.balance
            for a in after.accounts
            if a.id in original and a.wrapper == "cash"
        },
    )


def acquired(sleeve, when):
    data = sleeve.model_dump(mode="json")
    if data["private_fund_contract"] is not None:
        data["private_fund_contract"].update(
            federal_holding_start=when, federal_capital_character=None
        )
    return data


def new_capital(original, after):
    return {a.id: a.balance for a in after.accounts if a.id not in original}


def sleeve_capital(after, new):
    sleeves = {s.account_id for s in after.sleeve_plan.sleeves} if after.sleeve_plan else set()
    return {key: value for key, value in new.items() if key in sleeves}
