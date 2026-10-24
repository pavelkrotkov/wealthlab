"""A funded Roth needs the December loss to offset an external recognized gain."""

from wealthlab.household.scenario import Scenario
from wealthlab.portfolio.household_example import lot, plan
from wealthlab.retirement.ira_deposit_household_example import synthetic


def case(repurchase=False):
    data = synthetic().model_dump(mode="json")
    data["accounts"][0]["balance"] = "200000"
    data["incomes"][0]["monthly_amount"] = "18000"
    data["accounts"].append(
        dict(
            id="brokerage",
            provenance="illustration",
            owner="person_a",
            wrapper="taxable",
            currency="USD",
            balance="200000",
            monthly_fee="0",
        )
    )
    data["tax_plan"]["events"].append(
        dict(
            date="2026-03-01",
            description="Synthetic external allocated gain",
            cash_received="0",
            federal=dict(long_term="20000"),
            new_jersey=dict(dispositions="20000"),
        )
    )
    linked = plan(Scenario.model_validate(data))
    linked.update(year_end_wash_policy="january_reconcile", funding_sources=[])
    linked["case"]["lots"] = [lot("holding", "2000", "200000", "200000")]
    linked["case"]["closing_prices"] = dict(stock="100")
    for marks in linked["monthly_marks"]:
        marks["prices"] = dict(stock="100")
    linked["case"]["trades"] = [
        dict(
            id="loss",
            provenance="illustration",
            date="2026-12-20",
            action="sell",
            account_id="brokerage",
            security_id="stock",
            quantity="2000",
            price="90",
            commission="0",
            selection="hifo",
        )
    ]
    if repurchase:
        linked["case"]["trades"].append(
            dict(
                id="replacement",
                provenance="illustration",
                date="2027-01-10",
                action="buy",
                account_id="brokerage",
                security_id="stock",
                quantity="2000",
                price="90",
                commission="0",
            )
        )
    data["lot_plan"] = linked
    return Scenario.model_validate(data)
