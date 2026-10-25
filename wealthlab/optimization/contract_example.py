"""Fixed synthetic option and employer assets use actual exits on shared factor paths.

This adds $10,000 existing stock capital and $20,000 vested employer capital to
all candidates equally. The separate $80,000 contingent award is forfeited;
it is never opening spendable wealth. Source tax allocations remain supplied.
"""

from datetime import timedelta

from wealthlab.employment.compensation_termination_example import terminated
from wealthlab.household.calendar import months
from wealthlab.markets.example import asset
from wealthlab.markets.option_example import synthetic as options
from wealthlab.optimization.inputs import PolicySearch
from wealthlab.optimization.product_example import account, add_factor


def extend(case):
    if not case.household.synthetic:
        raise ValueError("The contract starter only extends synthetic examples.")
    if case.household.option_plan or case.household.compensation_plan:
        raise ValueError("The contract starter cannot replace existing option or employer plans.")
    data = case.model_dump(mode="json")
    household = data["household"]
    source = terminated().model_dump(mode="json")
    employer = next(a for a in source["accounts"] if a["id"] == "employer_fund")
    household["accounts"] += [account("options", "taxable"), employer]
    household["compensation_plan"] = source["compensation_plan"]
    plan, binding = option_terms(case.household)
    household["option_plan"] = plan
    data["binding"].update(options=binding, employers=[employer_binding()])
    extend_markets(data)
    return PolicySearch.model_validate(data)


def extend_markets(data):
    markets = [data["training"], data["validation"]]
    markets.extend(check["market"] for check in data["robustness"].values())
    for market in markets:
        for identity, role, volatility in (
            ("option_stock", "equity", 0.3),
            ("option_index", "equity", 0.18),
            ("employer", "employer", 0.35),
        ):
            add_factor(market, asset(identity, role, 0.04, volatility, 0))


def option_terms(scenario):
    household, _, binding = options(strategy="Covered call")
    plan = household.option_plan.model_dump(mode="json")
    case = plan["case"]
    case["holdings"].update(as_of=str(scenario.start), end=str(scenario.end - timedelta(days=1)))
    case["legs"][0].update(opened=str(scenario.start))
    # Keep the supplied expiry; after expiry the native stock book remains until
    # its actual horizon unwind. No later contracts or roll quotes are invented.
    opening = case["marks"][0]
    case["marks"] = [dict(opening, date=str(scenario.start))] + [
        dict(opening, date=str(end - timedelta(days=1)))
        for _, end in months(scenario.start, scenario.end)
    ]
    case["holdings"]["closing_prices"] = {"STOCK": opening["stock"]}
    chosen = binding.options.model_dump(mode="json")
    chosen.update(stock_factor="option_stock", index_factor="option_index")
    return plan, chosen


def employer_binding():
    return dict(
        account_id="employer_fund",
        factor="employer",
        return_convention="net_mark_return_no_separate_cash_yield",
        replace_entered_net_returns_confirmed=True,
        event_sequence_start=90000,
    )
