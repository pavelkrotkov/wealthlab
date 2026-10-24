"""Monthly tax accrual with real withholding, year-end settlement and delayed refunds."""

from decimal import Decimal

from wealthlab.tax import payments, prior_payments, recognition, state_deduction
from wealthlab.tax.annual import evaluate
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

    def __init__(self, plan, scenario):
        validate(plan, scenario)
        self.plan = plan
        self.funding = AccountFunding(plan, scenario)
        self.cases = {case.policy.year: case for case in plan.cases}
        self.result: dict = {}
        self.previous = None
        self.year = None
        self.outstanding = dict(federal=Decimal(0), new_jersey=Decimal(0))
        self.refunds = []

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

    def month(self, amounts, wallet, start, end, required_cash) -> dict:
        """Recognize this month's income, then pay only available cash.

        Payroll withholding follows cumulative calculated employee liability;
        income-tax withholding uses explicit user-entered wage percentages.
        Year-end settlement later reconciles the remaining tax balance.
        """
        self.start_year(start.year)
        received, taxable_refund = prior_payments.receive(self, wallet, end)
        prior_paid = prior_payments.pay(self, wallet)
        self.case = recognition.scheduled(self.case, amounts, self.plan.income_rules)
        event_cash = self.events(wallet, start, end)
        sold = self.funding.fund(self, wallet, required_cash, amounts, start, end)
        paid_after_sale = prior_payments.pay(self, wallet)
        result = evaluate(self.case)
        requested = payments.withholding_request(amounts, self.plan, result, start, end)
        before = self.case.payments
        self.case, paid = payments.pay(self.case, wallet, requested, self.plan.state_deduction_mode)
        estimates = (
            self.case.payments.federal_estimates
            - before.federal_estimates
            + self.case.payments.nj_estimates
            - before.nj_estimates
        )
        self.result = evaluate(self.case)
        return dict(
            social_security_cash=recognition.social_cash(amounts, self.plan.income_rules),
            tax_withheld=paid - estimates,
            tax_estimates_paid=estimates,
            tax_payment_gap=max(Decimal(0), sum(requested.values()) - paid),
            prior_tax_paid=prior_paid + paid_after_sale,
            funding_sale_proceeds=sold,
            tax_refund_received=received,
            taxable_state_refund=taxable_refund,
            tax_event_cash=event_cash,
        )

    def events(self, wallet, start, end) -> Decimal:
        cash = Decimal(0)
        for item in self.plan.events:
            if start <= item.date < end:
                self.case = recognition.event(self.case, item)
                wallet.deposit(item.cash_received)
                cash += item.cash_received
        return cash

    def close(self, wallet, start, end) -> dict:
        return dict(close_year(self, wallet, start, end), funding_basis=dict(self.funding.basis))
