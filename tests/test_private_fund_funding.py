"""Illiquidity and noncash taxable allocations affect real household safety, not paper reserves."""

from household_sleeve_cases import change
from private_fund_cases import fund, request

from wealthlab.household.projection import project
from wealthlab.markets.household_outcomes import funding


def spending(data):
    data["expenses"] = [
        dict(
            id="bill",
            provenance="illustration",
            start="2026-01-01",
            end="2026-02-01",
            monthly_amount="20000",
            currency="USD",
            annual_growth=0,
            category="essential",
        )
    ]


def test_locked_fund_cannot_fund_bill_and_later_receivable_is_not_available_early():
    case = fund(cash=0, requests=[request(20000)], lock_until="2026-02-01", settlement_days=1)
    rows = project(change(case, spending))
    assert rows[0]["essential_unfunded"] == 20000
    assert rows[1]["closing_cash"] == 0
    assert rows[2]["closing_cash"] == 20000
    assert not funding(rows)["funded"]


def test_non_cash_allocation_tax_bill_does_not_unlock_the_fund_or_invent_cash():
    def configure(data):
        data["sleeve_plan"]["sleeves"][0]["allocations"] = [
            dict(
                id="income",
                provenance="assumption",
                date="2026-01-01",
                federal=dict(short_term="100000"),
                new_jersey=dict(dispositions="100000"),
            )
        ]

    rows = project(change(fund(cash=0), configure))
    assert rows[-1]["tax_unfunded"] > 0
    assert rows[-1]["account_balances"]["sleeve"] == 100000
    assert sum(r["tax_event_cash"] for r in rows) == 0
    assert not funding(rows)["funded"]
