"""Executed cash, debt and tax bases; this ledger does not invent premium funding.

Terminal proceeds repay the entire stated policy debt before any cash is received.
A below-debt discharge needs additional legal assumptions and is rejected. The
ordinary loan book includes capitalized interest; tax investment is a separate
state, so repaying a previously taxed MEC loan cannot create a second cost basis.
"""

from dataclasses import dataclass
from decimal import Decimal

from wealthlab.products.life_contract_tax import LOANS, RECEIPTS, TERMINAL, additional, recognize
from wealthlab.products.life_illustration_flows import OUTFLOWS

ZERO = Decimal(0)


@dataclass
class PolicyBook:
    basis: Decimal | None
    loan: Decimal
    closed: bool = False

    def apply(self, contract, event):
        if self.closed:
            raise ValueError("The policy is already closed.")
        before_loan, before_basis = self.loan, self.basis
        external = self.cash(event)
        taxable, self.basis = recognize(contract, event, self.basis)
        state_income = state_recognition(event)
        return dict(
            id=event.id,
            date=event.date.isoformat(),
            kind=event.kind,
            amount=event.amount,
            external_cash=external,
            loan_before=before_loan,
            loan_after=self.loan,
            federal_basis_before=before_basis,
            federal_basis_after=self.basis,
            federal_ordinary_income=taxable,
            federal_additional_tax=additional(contract, event, taxable),
            nj_ordinary_income=state_income,
            closed=self.closed,
        )

    def cash(self, event):
        if event.kind in TERMINAL:
            return self.terminate(event.amount)
        if event.kind in LOANS:
            self.loan += event.amount
        if event.kind == "loan_principal_repayment":
            if event.amount > self.loan:
                raise ValueError("Policy loan repayment exceeds actual outstanding debt.")
            self.loan -= event.amount
        if event.kind in RECEIPTS or event.kind == "loan_advance":
            return event.amount
        return -event.amount if event.kind in OUTFLOWS else ZERO

    def terminate(self, gross):
        if gross < self.loan:
            raise ValueError(
                "Terminal settlement below debt needs a separate discharge-tax profile."
            )
        received = gross - self.loan
        self.loan, self.closed = ZERO, True
        return received


def state_recognition(event):
    if event.kind in RECEIPTS | LOANS | TERMINAL:
        return event.nj_ordinary_income
    if event.nj_ordinary_income:
        raise ValueError("NJ income overrides apply only to receipt/loan/termination events.")
    return ZERO
