"""Scale supplied monetary unit schedules while preserving all rates and legal assumptions.

This is an explicit proportional scenario assumption, not a deduction derived
from a trade return. The native annual engines still apply their household
limits to recognized totals, and actual fund distributions recover actual basis.
"""

from decimal import Decimal

from wealthlab.products.household_inputs import HouseholdSleeve


def scale(unit, count):
    data = unit.model_dump()
    case = data["case"]
    case["opening_equity"] *= count
    for order in case["redemptions"]:
        order["amount"] *= count
    for allocation in data["allocations"]:
        for key in ("federal", "new_jersey"):
            allocation[key] = monetary(allocation[key], count)
    if data["private_fund_contract"] is not None:
        scale_contract(data["private_fund_contract"], count)
    return HouseholdSleeve.model_validate(data)


def monetary(values, count):
    result = {}
    for key, value in values.items():
        if isinstance(value, Decimal):
            result[key] = value * count
        elif isinstance(value, dict):
            result[key] = monetary(value, count)
        else:
            result[key] = value
    return result


def scale_contract(contract, count):
    for key in ("federal_opening_basis", "new_jersey_opening_basis"):
        contract[key] *= count
    for order in contract["requests"]:
        order["amount"] *= count
    for adjustment in contract["basis_adjustments"]:
        for key in ("federal", "new_jersey"):
            adjustment[key] *= count
