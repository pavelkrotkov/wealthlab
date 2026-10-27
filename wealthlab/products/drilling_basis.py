"""Cash IDC and tangible acquisition pools prevent deductions on unfunded source costs.

Depletion is a separately supplied prelimited fact, rather than a percentage
inferred from a product label. No production allows no modeled depletion.
Independent basis reductions are capped at actual remaining funded balances.
"""

from decimal import Decimal

from wealthlab.household.calendar import money

ZERO = Decimal(0)


def funded_components(ledger, item, observation, row):
    if item.component == "idc":
        return dict.fromkeys(("federal", "nj"), row["paid_costs"]["idc_cost"])
    if item.component == "operating_loss":
        return dict.fromkeys(("federal", "nj"), max(ZERO, -row["net_operating_income"]))
    if item.component == "depreciation":
        return dict(ledger.tangible_basis)
    if not observation.production_units:
        return dict.fromkeys(("federal", "nj"), ZERO)
    return {
        key: max(getattr(item, key + "_requested"), getattr(item, key + "_basis_reduction"))
        for key in ("federal", "nj")
    }


def reduce_basis(bases, item, available):
    for key in bases:
        field = "at_risk_reduction" if key == "at_risk" else key + "_basis_reduction"
        maximum = max(available.values()) if key == "at_risk" else available[key]
        amount = min(getattr(item, field), maximum)
        bases[key] -= money(min(amount, bases[key]))
