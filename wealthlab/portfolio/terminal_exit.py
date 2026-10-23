"""A hypothetical sale of selected taxable accounts, with unsold holdings kept visible."""

from datetime import timedelta
from decimal import Decimal

from pydantic import Field

from wealthlab.household.records import Money
from wealthlab.portfolio.generated_orders import identity
from wealthlab.portfolio.policies import SalePolicy
from wealthlab.portfolio.policy_execution import execute
from wealthlab.tax.facts import TaxModel


class TerminalExit(TaxModel):
    account_ids: list[str] = Field(min_length=1)
    commission_per_trade: Money = Decimal(0)
    no_replacements_next30_days: bool = False


def validate_exit(case):
    plan = case.terminal_exit
    if plan is None:
        return
    accounts = {item.id: item for item in case.accounts}
    if len(plan.account_ids) != len(set(plan.account_ids)):
        raise ValueError("Terminal-exit account IDs must be unique.")
    for key in plan.account_ids:
        if key not in accounts or accounts[key].wrapper != "taxable":
            raise ValueError("Terminal exits currently require configured taxable accounts.")


def liquidate(case, book):
    plan = case.terminal_exit
    assert plan is not None
    decisions = []
    for account in plan.account_ids:
        for security in case.securities:
            policy = SalePolicy(
                id=identity(book, "terminal_exit", str(len(decisions))),
                provenance="assumption",
                date=case.end,
                account_id=account,
                security_id=security.id,
                mode="sell_all",
                prices=case.closing_prices,
                commission=plan.commission_per_trade,
            )
            decisions.append(execute(case, book, policy))
    end = case.end + timedelta(days=30) if plan.no_replacements_next30_days else case.end
    return decisions, end
