"""Payer-withheld cash is already paid tax, never spendable recipient cash.

Gross cash is independent of taxable income: a distribution can contain basis.
These entered actual amounts do not infer withholding rates or tax eligibility.
"""

from decimal import Decimal

from wealthlab.household.records import Money
from wealthlab.tax import state_deduction
from wealthlab.tax.facts import TaxModel


class SourceWithholding(TaxModel):
    gross_cash: Money
    federal_income_withheld: Money = Decimal(0)
    nj_withheld: Money = Decimal(0)

    @property
    def total(self):
        return self.federal_income_withheld + self.nj_withheld


def credit(case, source, mode):
    """Credit actual source payments once without drawing household cash again."""
    if source is None:
        return case
    values = case.payments.model_dump()
    values["federal_income_withheld"] += source.federal_income_withheld
    values["nj_withheld"] += source.nj_withheld
    payments = type(case.payments).model_validate(values)
    updated = case.model_copy(update={"payments": payments})
    return state_deduction.add(updated, source.nj_withheld, mode)


def receipt(item):
    source = item.withholding
    return dict(
        date=item.date.isoformat(),
        description=item.description,
        gross_cash=source.gross_cash,
        net_cash=item.cash_received,
        federal_income_withheld=source.federal_income_withheld,
        nj_withheld=source.nj_withheld,
        total_withheld=source.total,
    )
