"""Denied distribution character is supplied explicitly, never inferred from lock length."""

from exchange_fund_cases import change, flat

from wealthlab.household.calendar import months
from wealthlab.household.funding import Wallet
from wealthlab.products.exchange_fund_household import Ledger


def test_denied_distribution_preserves_explicit_short_term_capital_character():
    def configure(data):
        data["exchange_fund_plan"].update(
            federal_basket_distribution="denied", federal_distribution_character="short_term"
        )

    case = change(flat(), configure)
    ledger, wallet = Ledger(case), Wallet(case)
    events = [
        event
        for start, end in months(case.start, case.end)
        for event in ledger.after_receipts(wallet, start, end)
    ]
    assert sum(e.federal.short_term for e in events) == 80000
    assert sum(e.federal.long_term for e in events) == 0
    assert sum(d["federal_gross_gain"] for d in ledger.book.disposals) == 0
