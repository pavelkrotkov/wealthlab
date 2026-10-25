"""Monthly tax accrual with real withholding, year-end settlement and delayed refunds."""

from decimal import Decimal
from itertools import chain

from wealthlab.tax import (
    foreign_tax_household,
    nj_residence_household,
    prior_payments,
    projection_monthly,
    recognition,
    required_funding,
    source_withholding,
    state_deduction,
)
from wealthlab.tax.funding_accounts import AccountFunding
from wealthlab.tax.projection_validation import validate
from wealthlab.tax.settlement import close_year


class TaxLedger:
    """One mutable ledger per immutable scenario run.

    The annual case holds cumulative recognized income and actual payments.
    Opening facts are already reflected in cash and are never deposited again.
    Prior-year unpaid tax remains owed; refunds stay separate until their dated
    receipt. Federal and NJ carry character survives the annual reset.
    """

    def __init__(self, plan, scenario, lots=None):
        validate(plan, scenario)
        self.plan = plan
        self.foreign = foreign_tax_household.make(scenario)
        self.lots = lots
        self.provisional_returns = set()
        self.preserve_ira_elections = (
            lots is not None and lots.plan.year_end_wash_policy == "january_reconcile"
        )
        self.funding = AccountFunding(plan, scenario)
        if lots is not None:
            from wealthlab.portfolio.household_funding import Funding

            self.funding = Funding(self.funding, lots)
        self.cases = {case.policy.year: case for case in plan.cases}
        self.result: dict = {}
        self.previous = None
        self.year = None
        self.outstanding = dict(federal=Decimal(0), new_jersey=Decimal(0))
        self.refunds = []
        self.refund_receipts = []
        self.closed_returns = {}
        self.source_receipts = []

    @property
    def owed(self):
        return sum(self.outstanding.values(), Decimal(0))

    def start_year(self, year):
        if self.year == year:
            return
        self.year = year
        case = self.cases[year]
        if self.previous is not None:
            federal = case.federal_income.model_copy(
                update={
                    "short_carry": self.previous["federal"]["short_carry"],
                    "long_carry": self.previous["federal"]["long_carry"],
                }
            )
            business = case.nj_income.business.model_copy(
                update={"carry": self.previous["new_jersey"]["business_carry"]}
            )
            case = case.model_copy(
                update={
                    "federal_income": federal,
                    "nj_income": case.nj_income.model_copy(update={"business": business}),
                }
            )
        self.case = state_deduction.add(
            case, state_deduction.nj_paid(case), self.plan.state_deduction_mode
        )

    def month(
        self,
        amounts,
        wallet,
        start,
        end,
        required_cash,
        extra_events=(),
        receipt_hook=None,
        pre_receipt_hook=None,
        additional_nj_wages=Decimal(0),
    ) -> dict:
        """Recognize this month's income, then pay only available cash.

        Payroll withholding follows cumulative calculated employee liability;
        Income-tax withholding uses entered wage rates; year-end settlement reconciles tax.
        """
        self.source_receipts = []
        required_funding.begin(self, amounts, required_cash, start, end)
        self.nj_wage_withholding_addition = additional_nj_wages
        self.start_year(start.year)
        self.case = nj_residence_household.observe(self.case, end)
        received, taxable_refund = prior_payments.receive(self, wallet, end)
        self.case = recognition.scheduled(self.case, amounts, self.plan.income_rules)
        event_cash = self.events(wallet, start, end, extra_events)
        if pre_receipt_hook is not None:
            event_cash += self.apply_events(
                wallet, start, end, pre_receipt_hook(wallet, start, end)
            )
        prior_paid = prior_payments.pay(self, wallet)
        foreign_tax_household.before_optional(self, wallet, start, end)
        if receipt_hook is not None:
            event_cash += self.apply_events(wallet, start, end, receipt_hook(wallet, start, end))
        # The shared quote observes wrapper reductions and earlier product sales.
        self.fund_required(wallet, Decimal(0), start, end)
        paid_after_sale = prior_payments.pay(self, wallet)
        foreign_tax_household.reconcile_required(self, wallet, start, end)
        paid, estimates = projection_monthly.pay_current(self, wallet, amounts, start, end)
        return projection_monthly.report(
            self,
            amounts,
            start,
            end,
            paid,
            estimates,
            prior_paid + paid_after_sale,
            received,
            taxable_refund,
            event_cash,
        )

    def fund_required(self, wallet, additional, start, end):
        """Fund actual required cash with the same tax, basis and source restrictions."""
        return required_funding.fund(self, wallet, additional, start, end)

    def events(self, wallet, start, end, extra_events=()) -> Decimal:
        return self.apply_events(wallet, start, end, chain(self.plan.events, extra_events))

    def apply_events(self, wallet, start, end, items) -> Decimal:
        cash = Decimal(0)
        for item in items:
            if start <= item.date < end:
                source_withholding.validate_foreign_book(item, self.foreign)
                self.case = recognition.event(self.case, item, self.plan.state_deduction_mode)
                if item.withholding is not None:
                    self.source_receipts.append(source_withholding.receipt(item))
                wallet.deposit(item.cash_received)
                cash += item.cash_received
        return cash

    def close(self, wallet, start, end) -> dict:
        provisional = self.lots is not None and self.lots.pending(start.year)
        if end.year > start.year and provisional:
            self.provisional_returns.add(start.year)
        return dict(
            close_year(self, wallet, start, end),
            funding_basis=dict(self.funding.basis),
            tax_return_provisional=bool(provisional),
        )
