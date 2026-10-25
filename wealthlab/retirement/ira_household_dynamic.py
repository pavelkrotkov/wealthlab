"""Reconcile fixed IRA schedules using actual funded deposits and incoming plan cash.

Only known funded deposits/rollovers enter the annual engine. Its later scheduled
withdrawals/returns never supply earlier account balances or spending cash.
Annual basis and deduction results enter December; prior months remain
explicitly unfinalized. Tax settlement gains are included in the final
eligibility check before any projection result is returned.
"""

from datetime import date

from wealthlab.retirement.distribution_inputs import DistributionCase
from wealthlab.retirement.distributions import run
from wealthlab.retirement.ira_contribution_tax import check_completed
from wealthlab.retirement.ira_household import (
    apply_balances,
    summarize,
    tax_event,
    withdrawal_events,
)
from wealthlab.retirement.ira_household_compile import annual_case, carry_owners, opening_accounts
from wealthlab.retirement.ira_household_deposit_funding import Funding
from wealthlab.retirement.ira_household_deposit_validation import annual_case as deposit_case
from wealthlab.retirement.ira_household_deposit_validation import validate as validate_deposits
from wealthlab.retirement.ira_household_validation import validate


class Ledger:
    def __init__(self, scenario):
        validate(scenario)
        if scenario.ira_plan.contributions is not None:
            validate_deposits(scenario)
        self.plan = scenario.ira_plan
        self.owners = self.plan.owners
        self.accounts = opening_accounts(scenario)
        self.funding = Funding(self.plan.contributions)
        self.rollovers = []
        self.summary = {}
        self.year = scenario.start.year
        self.closed_years = {}
        self.cache_key: tuple[int, int, int] | None = None

    def refresh(self, year):
        # Per-projection fixed schedules; actual deposits/rollovers are append-only.
        key = (year, len(self.funding.orders), len(self.rollovers))
        if key == self.cache_key:
            return
        self.year = year
        self.context = self.contribution_context(year)
        base = annual_case(self.plan, self.owners, self.accounts, year)
        self.case = DistributionCase.model_validate(
            dict(
                **base.model_dump(
                    exclude={
                        "contributions",
                        "contribution_context_confirmed",
                        "incoming_rollovers",
                    }
                ),
                contributions=self.context,
                contribution_context_confirmed=True,
                incoming_rollovers=[r for r in self.rollovers if r.date.year == year],
            )
        )
        self.result = run(self.case)
        self.cache_key = key

    def contribution_context(self, year):
        if self.plan.contributions is None:
            return None
        context = next(y for y in self.plan.contributions.years if y.year == year)
        orders = [o for o in self.funding.orders if o.date.year == year]
        receipts = [r for r in self.funding.receipts if r["date"].year == year]
        return deposit_case(context, self.accounts, orders, receipts)

    def month(self, wallet, start, end):
        self.refresh(start.year)
        apply_balances(self.result, wallet, start, end)
        orders = [r for r in self.result["orders"] if start <= r["date"] < end]
        self.summary = {}
        return withdrawal_events(orders), summarize(orders, end == date(start.year + 1, 1, 1))

    def after_receipts(self, wallet, start, end):
        self.summary.update(self.funding.month(self.context, wallet, start, end))
        self.refresh(start.year)
        apply_balances(self.result, wallet, start, end)
        if end == date(start.year + 1, 1, 1):
            return (tax_event(self.result, self.owners),)
        return ()

    def completed(self, taxes, end):
        if end != date(self.year + 1, 1, 1):
            return self.summary
        if self.context is not None:
            self.closed_years[self.year] = (
                self.context,
                self.result["orders"],
                self.result["contribution_owners"],
            )
        checked = self.check_year(taxes)
        self.result["contribution_eligibility"] = checked
        self.summary.update(
            ira_annual_reconciliation=self.result,
            ira_contribution_eligibility=checked,
            ira_contribution_audit=list(self.funding.audit),
        )
        self.owners = carry_owners(self.owners, self.result)
        self.accounts = [
            a.model_copy(update=dict(balance=self.result["account_balances"][a.id]))
            for a in self.accounts
        ]
        return self.summary

    def check_year(self, taxes):
        if self.context is None:
            return dict(status="no_regular_ira_contributions_modeled")
        if self.year in taxes.provisional_returns:
            return dict(status="pending_january_wash_reconciliation", year=self.year)
        return check_completed(
            self.context,
            self.result["orders"],
            self.result["contribution_owners"],
            taxes.case.federal_income,
            taxes.result["federal"],
            allow_underclaim=taxes.preserve_ira_elections,
        )
