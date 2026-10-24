"""Supplied recognition can create tax without cash and never deposits a hypothetical saving."""

from household_sleeve_cases import change, flat

from wealthlab.household.projection import project


def test_supplied_capital_allocation_enters_one_return_without_cash_receipt():
    def configure(data):
        data["sleeve_plan"]["sleeves"][0]["allocations"] = [
            dict(
                id="supplied_gain",
                provenance="assumption",
                date="2026-04-01",
                federal=dict(short_term="50000"),
                new_jersey=dict(dispositions="50000"),
            )
        ]

    rows = project(change(flat(), configure))
    assert rows[-1]["annual_tax"]["federal"]["agi"] == 50000
    assert sum(r["tax_event_cash"] for r in rows) == 0
    assert rows[-1]["account_balances"]["sleeve"] == 100000
    tax = rows[-1]["annual_tax"]["total_liability"]
    assert rows[-1]["net_wealth"] == 110000 - tax


def test_source_observations_and_tax_allocations_remain_unchanged():
    case = flat()
    original = case.model_dump_json()
    project(case)
    assert case.model_dump_json() == original
