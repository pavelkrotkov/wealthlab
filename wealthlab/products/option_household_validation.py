"""Account ownership, actual-cash and complete tax assumptions precede household execution."""

from wealthlab.products.household_accounts import excluded_accounts, validate_type
from wealthlab.products.option_household_scope import validate_calendar, validate_tax
from wealthlab.products.option_validation import validate as validate_case


def validate(scenario, market):
    plan = scenario.option_plan
    validate_dependencies(scenario, market)
    validate_case(plan.case)
    validate_confirmations(plan)
    account = next((a for a in scenario.accounts if a.id == plan.account_id), None)
    validate_type(account)
    forbidden = excluded_accounts(scenario)
    if scenario.sleeve_plan:
        forbidden.update(s.account_id for s in scenario.sleeve_plan.sleeves)
    if plan.account_id in forbidden:
        raise ValueError(
            "Options cannot share another book, transfer or generic tax funding account."
        )
    validate_opening(plan, account)
    validate_calendar(plan.case, scenario)
    validate_tax(plan.case)


def validate_confirmations(plan):
    if not (
        plan.actual_household_cash_confirmed and plan.tax_history_and_no_duplicate_income_confirmed
    ):
        raise ValueError("Confirm actual cash and complete nonduplicated option tax history.")


def validate_opening(plan, account):
    """The opening household account already owns the stock and inside cash.

    An extra standalone reserve would count the same funding capacity twice.
    """
    case = plan.case
    book = case.holdings
    opening = book.accounts[0].cash + sum(lot.quantity for lot in book.lots) * case.marks[0].stock
    if account.balance != opening or case.outside_cash != 0:
        raise ValueError("Reconcile option account stock/cash and use zero separate outside cash.")
    if book.accounts[0].id != plan.account_id:
        raise ValueError("The option lot-book account must match its household account ID.")


def validate_dependencies(scenario, market):
    if market is not None:
        raise ValueError(
            "Options need explicit dated marks; generated market binding is unfinished."
        )
    if scenario.tax_plan is None:
        raise ValueError("Household options require a complete household tax plan.")
    plan = scenario.option_plan
    if plan.case.dividends and not plan.ordinary_dividend_tax_on_cash_receipt_confirmed:
        raise ValueError(
            "Confirm ordinary dividend tax at cash receipt; special timing is unsupported."
        )
