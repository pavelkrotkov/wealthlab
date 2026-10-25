"""State income ingredients stay separate from federal exemption and inside-HSA assets.

Raw lot gains use the separately supplied NJ basis. They are recognized only
under the declared taxable-securities/no-wash assumption, not as a legal
eligibility finding. The household return later limits and combines categories.
"""

from copy import deepcopy
from datetime import date
from decimal import Decimal

from wealthlab.household.calendar import money
from wealthlab.portfolio.fees import summary as fee_summary
from wealthlab.portfolio.household_values import account_value

ZERO = Decimal(0)


def income(ledger, year):
    result = dict(interest=ZERO, dividends=ZERO, dispositions=ZERO)
    for row in ledger.book.disposals:
        if date.fromisoformat(row["date"]).year == year:
            result["dispositions"] += row["nj_gross_gain"]
    events = {d.id: d for d in ledger.plan.case.distributions}
    for row in ledger.book.distributions:
        event = events[row["distribution"]]
        if (
            row["recognized"]
            and event.recognition_date.year == year
            and event.nj_character != "exempt"
        ):
            result[event.nj_character] += row["amount"]
    return result


def values(ledger):
    return {
        key: account_value(ledger.book.lots.values(), key, cash, ledger.prices)
        for key, cash in ledger.book.cash.items()
    }


def receivables(ledger):
    result = dict.fromkeys(ledger.book.accounts, ZERO)
    for row in ledger.book.distributions:
        if not row["paid"]:
            result[row["account_id"]] += row["amount"]
    return result


def snapshot(ledger):
    gross, due = values(ledger), receivables(ledger)
    fees = fee_summary(ledger.book)
    return deepcopy(
        dict(
            as_of=ledger.when,
            gross_account_values=gross,
            cash_by_account=dict(ledger.book.cash),
            distribution_receivable=due,
            fee_summary=fees,
            fee_owed_by_account=dict(ledger.book.fee_owed),
            net_wealth=money(sum(gross.values()) + sum(due.values()) - fees["cash_owed"]),
            quoted_prices=dict(ledger.prices),
            lots=[lot.model_dump(mode="json") for lot in ledger.book.lots.values()],
            disposals=ledger.book.disposals,
            distributions=ledger.book.distributions,
            executed_trades=[t.model_dump(mode="json") for t in ledger.book.history],
            cash_targets=ledger.targets,
            nj_income_by_year={
                year: income(ledger, year)
                for year in range(ledger.plan.case.as_of.year, ledger.when.year + 1)
            },
            federal_investment_income=ZERO,
            transaction_costs=sum((t.commission for t in ledger.book.history), ZERO),
            nj_treatment=ledger.plan.nj_treatment,
        )
    )
