"""Flat native employer/stock paths isolate supplied vesting and actual tax cash.

Opening320000 contains only20000 vested employer value.80000 is contingent.
Zero commissions keep an unrelated late tax-loss refund outside this cash oracle.
"""

from wealthlab.optimization.employment_example import synthetic
from wealthlab.optimization.inputs import PolicySearch


def flat():
    data = synthetic().model_dump(mode="json")
    data["targets"].update(target_age=50, reserve_years=0, maximum_issuer_weight=None)
    for market in (data["training"], data["validation"]):
        market.update(paths=1, expected_annual_inflation=0, annual_inflation_volatility=0)
        for factor in market["assets"]:
            factor.update(expected_annual_mark_return=0, annual_volatility=0, annual_cash_yield=0)
    book = data["household"]["lot_plan"]["case"]
    for lot in book["lots"]:
        lot["federal_basis"] = lot["nj_basis"] = str(int(lot["quantity"]) * 100)
    book["sale_policies"][0]["commission"] = "0"
    return PolicySearch.model_validate(data)


def changed(edit):
    data = flat().model_dump(mode="json")
    edit(data)
    return PolicySearch.model_validate(data)
