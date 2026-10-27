"""Flat prices and full basis give an independent cash identity for every actual candidate."""

from wealthlab.optimization.example import synthetic
from wealthlab.optimization.inputs import PolicySearch


def flat():
    data = synthetic().model_dump(mode="json")
    data["targets"]["target_age"] = 50
    for market in (data["training"], data["validation"]):
        market.update(paths=1, expected_annual_inflation=0, annual_inflation_volatility=0)
        market["assets"][0].update(
            expected_annual_mark_return=0, annual_volatility=0, annual_cash_yield=0
        )
    for lot in data["household"]["lot_plan"]["case"]["lots"]:
        lot["federal_basis"] = lot["nj_basis"] = str(int(lot["quantity"]) * 100)
    return PolicySearch.model_validate(data)


def changed(case, edit):
    data = case.model_dump(mode="json")
    edit(data)
    return PolicySearch.model_validate(data)
