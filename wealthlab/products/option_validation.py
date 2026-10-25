"""Validate the bounded option book and complete dated source coverage."""

from wealthlab.portfolio.validation import validate as validate_lots
from wealthlab.products.option_event_validation import validate_events
from wealthlab.products.option_leg_validation import validate_leg


def validate(case):
    """The lot engine validates source identity before option-specific restrictions.

    Date coverage avoids interpolated exercise or invented year-end quotes.
    Reserved trade identifiers protect the lot lineage during physical delivery.
    """
    validate_lots(case.holdings)
    validate_book(case.holdings)
    dates = [mark.date for mark in case.marks]
    if (
        dates != sorted(set(dates))
        or dates[0] != case.holdings.as_of
        or dates[-1] != case.holdings.end
    ):
        raise ValueError("Ordered unique marks must cover the exact opening and ending dates.")
    validate_ids(case)
    for leg in case.legs:
        validate_leg(case, leg, dates)
    validate_events(case, dates)
    validate_dividends(case, dates)


def validate_book(book):
    if len(book.accounts) != 1 or book.accounts[0].wrapper != "taxable":
        raise ValueError("Options require one explicit taxable USD account.")
    if [s.id for s in book.securities] != ["STOCK"] or book.trades:
        raise ValueError("Option book requires STOCK and no independent trades/policies.")
    forbidden = [
        book.sale_policies,
        book.harvest_policies,
        book.fee_schedules,
        book.distributions,
        book.federal_wash_tracking,
        book.nj_wash_treatment == "federal_rules",
        book.terminal_exit,
        book.lot_tax_cases,
    ]
    if any(forbidden):
        raise ValueError("Use option-specific events, dividends, fees and conditional tax paths.")


def validate_dividends(case, dates):
    for item in case.dividends:
        if item.ex_date not in dates or item.pay_date not in dates or item.pay_date < item.ex_date:
            raise ValueError("Dividends require dated marks and chronological entitlement.")


def validate_ids(case):
    """Generated IDs share the lot namespace because exercise purchases create real lots.

    Check the complete input before making the first premium payment.
    """
    ids = [leg.id for leg in case.legs]
    if len(ids) != len(set(ids)) or set(ids) & {lot.id for lot in case.holdings.lots}:
        raise ValueError("Option leg IDs must be unique and distinct from lot IDs.")
    reserved = {f"exercise_{leg.id}" for leg in case.legs} | {"complete_unwind"}
    if reserved & {lot.id for lot in case.holdings.lots}:
        raise ValueError("Opening lot IDs collide with generated delivery or unwind trades.")
