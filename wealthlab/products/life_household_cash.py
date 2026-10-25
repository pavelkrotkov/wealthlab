"""Execute each policy event against actual cash; failed payments use supplied exits."""

from decimal import Decimal

from wealthlab.products.life_illustration_flows import OUTFLOWS
from wealthlab.tax.facts import FederalIncome
from wealthlab.tax.nj_facts import NJIncome
from wealthlab.tax.projection_inputs import TaxEvent

ZERO = Decimal(0)


def execute(ledger, holding, event, wallet, start, end):
    requested = event.amount if event.kind in OUTFLOWS else ZERO
    if requested and holding.funding == "permitted_household_sales":
        ledger.tax.fund_required(wallet, requested, start, end)
    if wallet.cash < requested:
        failure = holding.failure_exits[event.id]
        actual, source, paid = failure.event, failure.withholding, ZERO
    else:
        actual, source, paid = event, holding.withholding.get(event.id), wallet.pay(requested)
    book = ledger.books[holding.account_id]
    row = book.apply(holding.contract, actual)
    row.update(
        account_id=holding.account_id,
        requested_event=event.id,
        requested_kind=event.kind,
        payment_requested=requested,
        payment_paid=paid,
        payment_unfunded=requested - paid,
        failure_exit=actual is not event,
    )
    return row, tax_event(row, actual, source)


def tax_event(row, event, source):
    fields = ("federal_ordinary_income", "federal_additional_tax", "nj_ordinary_income")
    if any(row[field] is None for field in fields):
        raise ValueError("Actual policy path has unresolved tax recognition.")
    gross = max(ZERO, row["external_cash"])
    if source is not None and source.gross_cash != gross:
        raise ValueError("Policy withholding gross cash must equal the actual net-of-loan receipt.")
    withheld = source.total if source is not None else ZERO
    row.update(source_tax_withheld=withheld, received_cash=gross - withheld)
    return TaxEvent(
        date=event.date,
        description=f"Life policy {row['account_id']}: {event.kind}",
        cash_received=gross - withheld,
        federal=FederalIncome(
            insurance_ordinary_income=row["federal_ordinary_income"],
            insurance_additional_tax=row["federal_additional_tax"],
        ),
        new_jersey=NJIncome(other=row["nj_ordinary_income"]),
        withholding=source,
    )
