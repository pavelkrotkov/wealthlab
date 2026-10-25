"""The liquid alternative uses actual shares under the same requested capital budget.

Drilling creditors and K-1 facts belong to the drilling strategy. The reference
has explicit separate cash requests and actual capital-gain recognition; no
well-specific expense or tax allocation is silently copied onto ETF shares.
"""

from decimal import Decimal

from wealthlab.household.calendar import money
from wealthlab.products.drilling_reference_book import opening as opening
from wealthlab.products.drilling_reference_tax import recognition_date, recognize
from wealthlab.products.drilling_reference_trade import fund, sell

ZERO = Decimal(0)
SECURITY = "drilling_reference_security"


def advance(ledger, observation, wallet):
    plan, book = ledger.plan, ledger.reference_book
    funded = fund(ledger, observation, wallet)
    ledger.reference_exit_pending |= observation.exit_requested
    cash_request = observation.reference_cash_request
    sell(ledger, observation, cash_request)
    swept = sum(book.cash.values(), ZERO)
    wallet.deposit(swept)
    book.cash = dict.fromkeys(book.cash, ZERO)
    value = sum(
        (money(lot.quantity * observation.reference_price) for lot in book.lots.values()), ZERO
    )
    wallet.balances[plan.account_id] = value
    blocked = ledger.reference_exit_pending and bool(book.lots)
    row = dict(
        date=observation.date.isoformat(),
        call_funded=funded,
        recourse_funded=ZERO,
        call_owed=ledger.call_owed,
        production_receipts=ZERO,
        royalties=ZERO,
        net_operating_income=ZERO,
        distribution=ZERO if ledger.reference_exit_pending else swept,
        distribution_unfilled=max(ZERO, cash_request - swept),
        exit_cash=swept if ledger.reference_exit_pending else ZERO,
        blocked_exit=blocked,
        account_value=value,
        recourse_liability=ZERO,
        creditor_payables=ZERO,
        cash=ZERO,
        property_value=value,
        product_failure=bool(ledger.call_owed or blocked),
    )
    recognize_at = recognition_date(ledger, observation)
    tax_event = recognize(ledger, observation.date, recognize_at)
    return row, [tax_event]
