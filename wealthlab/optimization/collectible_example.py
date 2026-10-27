"""Original gold-as-collectible sale choices reuse actual lots and the shared tax book.

Classification is an explicit illustration, not a claim about any gold fund.
The $100,000 existing position and separate bases replace the starter stock;
no capital is added. A zero-yield price factor supplies marks only.
"""

from wealthlab.optimization.example import synthetic as base
from wealthlab.optimization.inputs import PolicySearch


def synthetic():
    data = base().model_dump(mode="json")
    household = data["household"]
    household["name"] = "Synthetic gold treated as collectible; conditional classification"
    household["members"][0]["retirement_date"] = "2030-01-01"
    household["incomes"][0]["monthly_amount"] = "50000"
    plan = household["lot_plan"]
    book = plan["case"]
    book["securities"][0].update(
        id="gold", kind="collectible", wash_group="gold", exposure_group="gold"
    )
    for lot in book["lots"]:
        lot["security_id"] = "gold"
    for owner, key in ((book, "closing_prices"), (plan, "opening_prices")):
        owner[key] = dict(gold="100")
    for mark in plan["monthly_marks"]:
        mark["prices"] = dict(gold="100")
    plan["funding_sources"][0]["security_id"] = "gold"
    exit_order = dict(book["sale_policies"][0], security_id="gold", prices=dict(gold="100"))
    book["sale_policies"] = [exit_order]
    data["binding"]["securities"][0].update(security_id="gold", factor="gold_price")
    for market in (data["training"], data["validation"]):
        market["assets"][0].update(
            id="gold_price",
            role="other",
            annual_cash_yield=0,
            expected_annual_mark_return=0.02,
            annual_volatility=0.15,
        )
    data["dimensions"] = [
        dict(
            id="gold_sale",
            choices=[
                dict(id="early", sale_policies=[dict(exit_order, date="2026-01-31")]),
                dict(id="later", sale_policies=[exit_order]),
            ],
        )
    ]
    return PolicySearch.model_validate(data)
