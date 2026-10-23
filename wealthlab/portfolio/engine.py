"""Lot accounting and optional federal wash tracking, independent of tax cash funding."""

from copy import deepcopy
from decimal import Decimal

from wealthlab.household.calendar import money
from wealthlab.portfolio.book import Book
from wealthlab.portfolio.concentration import summarize
from wealthlab.portfolio.harvest_comparison import compare, loss_summary
from wealthlab.portfolio.nj_recognition import finish as finish_nj
from wealthlab.portfolio.policy_execution import replay
from wealthlab.portfolio.tax_reporting import report
from wealthlab.portfolio.terminal_exit import liquidate
from wealthlab.portfolio.validation import validate


def run(case) -> dict:
    result = project(case)
    if case.compare_harvesting:
        off_case = case.model_copy(update={"harvest_policies": [], "compare_harvesting": False})
        result["harvest_comparison"] = compare(result, project(off_case))
    return result


def project(case):
    validate(case)
    book = Book(case)
    decisions = replay(case, book)
    result = snapshot(case, book, decisions, case.end)
    result["harvest_loss_summary"] = loss_summary(result)
    if case.terminal_exit is not None:
        exit_book = deepcopy(book)
        exit_decisions, recognition_end = liquidate(case, exit_book)
        result["terminal_exit"] = snapshot(case, exit_book, exit_decisions, recognition_end)
        result["terminal_exit_assumptions"] = case.terminal_exit.model_dump(mode="json")
    return result


def snapshot(case, book, decisions, recognition_end):
    book.wash.finish(book, recognition_end)
    finish_nj(case, book, recognition_end)
    values = {key: Decimal(0) for key in book.securities}
    for lot in book.lots.values():
        values[lot.security_id] += lot.quantity * case.closing_prices[lot.security_id]
    cash = sum(book.cash.values(), Decimal(0))
    wealth = cash + money(sum(values.values(), Decimal(0)))
    return dict(
        cash_by_account=book.cash,
        closing_cash=cash,
        security_values={key: money(value) for key, value in values.items()},
        gross_wealth=wealth,
        concentration=summarize(case, book, values, wealth),
        lots=[lot.model_dump(mode="json") for lot in book.lots.values()],
        disposals=book.disposals,
        harvest_decisions=book.harvest_decisions,
        harvest_sales=sorted(book.harvest_sales),
        sale_decisions=decisions,
        executed_trades=[trade.model_dump(mode="json") for trade in book.history],
        transaction_costs=sum((trade.commission for trade in book.history), Decimal(0)),
        annual_tax_comparison=report(case, book),
        nj_wash_treatment=case.nj_wash_treatment,
        scope=(
            "Federal wash tracking enabled; NJ recognition follows the explicit treatment choice. "
            "Household tax benefit and funding are not integrated yet."
            if case.federal_wash_tracking
            else "Gross lot accounting; wash adjustment and tax-funded sale modeling are disabled."
        ),
    )
