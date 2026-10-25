"""A $1,000 stock position has independent $100 federal and $200 NJ basis."""

from wealthlab.household.scenario import Scenario
from wealthlab.markets.rebalance_example import synthetic
from wealthlab.portfolio.book import Book


def payload():
    scenario, _, _ = synthetic()
    data = scenario.model_dump(mode="json")
    data.update(incomes=[], expenses=[])
    data["tax_plan"]["income_rules"] = []
    data["accounts"][1]["balance"] = "1000"
    linked = data["lot_plan"]
    lot = linked["case"]["lots"][0]
    lot.update(quantity="10", federal_basis="100", nj_basis="200")
    linked["case"]["lots"] = [lot]
    linked["case"]["closing_prices"] = dict(stock="100", bond="100")
    for mark in linked["monthly_marks"]:
        mark["prices"] = dict(stock="100", bond="100")
    linked["rebalances"] = [dict(linked["rebalances"][0], commission_per_trade="0")]
    return data


def book_case(**changes):
    data = payload()
    data["lot_plan"]["rebalances"][0].update(changes)
    plan = Scenario.model_validate(data).lot_plan
    assert plan is not None
    return Book(plan.case), plan.rebalances[0], plan.opening_prices
