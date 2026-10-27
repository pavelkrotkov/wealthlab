"""Cash, one and two supplied covered-call units share the same original capital.

Quotes and prices here are invented. The native book actually buys the shares;
the initial $12,000 unit includes its cash reserve, never historical stock lots.
"""

from datetime import timedelta

from wealthlab.household.calendar import months
from wealthlab.markets.example import asset
from wealthlab.optimization.inputs import PolicySearch
from wealthlab.optimization.product_example import add_factor
from wealthlab.products.option_purchase_example import unit_plan


def extend(case):
    if not case.household.synthetic:
        raise ValueError("The option allocation starter only extends synthetic examples.")
    if case.household.option_plan or case.option_opportunity:
        raise ValueError("The allocation starter requires no existing option book or opportunity.")
    data = case.model_dump(mode="json")
    data["option_opportunity"] = opportunity(case)
    data["dimensions"].append(
        dict(
            id="new_option_purchase",
            choices=[
                dict(id=name, option_units=count)
                for name, count in (("cash", 0), ("one", 1), ("two", 2))
            ],
        )
    )
    for market in [
        data["training"],
        data["validation"],
        *(c["market"] for c in data["robustness"].values()),
    ]:
        add_factor(market, asset("option_stock", "equity", 0.04, 0.3, 0))
        add_factor(market, asset("option_index", "equity", 0.04, 0.18, 0))
    return PolicySearch.model_validate(data)


def opportunity(case):
    scenario = case.household
    unit = unit_plan().model_dump(mode="json")
    native = unit["case"]
    native["holdings"].update(as_of=str(scenario.start), end=str(scenario.end - timedelta(days=1)))
    native["opening_stock_purchase"]["date"] = str(scenario.start)
    for leg in native["legs"]:
        leg["opened"] = str(scenario.start)
    opening = native["marks"][0]
    native["marks"] = [dict(opening, date=str(scenario.start))] + [
        dict(opening, date=str(end - timedelta(days=1)))
        for _, end in months(scenario.start, scenario.end)
    ]
    native["holdings"]["closing_prices"] = {"STOCK": opening["stock"]}
    source = next(a for a in scenario.accounts if (a.wrapper, a.currency) == ("cash", "USD"))
    return dict(
        id="new_covered_calls",
        provenance="illustration",
        cash_account=source.id,
        owner="joint",
        unit=unit,
        minimum_units=0,
        maximum_units=5,
        opening_cash_purchase_assumed_confirmed=True,
        per_unit_absolute_fees_confirmed=True,
        binding=dict(
            account_id=unit["account_id"],
            stock_factor="option_stock",
            index_factor="option_index",
            rate=0.04,
            stock_vol=0.2,
            index_vol=0.2,
            stock_yield=0,
            index_yield=0,
            replace_dated_marks_confirmed=True,
            hypothetical_model_execution_confirmed=True,
        ),
    )
