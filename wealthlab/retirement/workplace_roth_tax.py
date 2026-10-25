"""Withholding consumes only taxable Roth cash; state classification is an explicit assumption."""

from decimal import Decimal

from wealthlab.household.calendar import money
from wealthlab.tax.facts import FederalIncome
from wealthlab.tax.nj_facts import NJIncome
from wealthlab.tax.nj_retirement import RetirementEligibility
from wealthlab.tax.projection_inputs import TaxEvent
from wealthlab.tax.source_withholding import SourceWithholding

ZERO = Decimal(0)


def withholding(order, gross, recognized):
    federal = money(recognized["federal_taxable"] * order.federal_withholding_rate)
    nj = min(money(recognized["nj_taxable"] * order.nj_withholding_rate), gross - federal)
    return SourceWithholding(gross_cash=gross, federal_income_withheld=federal, nj_withheld=nj)


def tax_event(order, row, born):
    return TaxEvent(
        date=order.date,
        description=f"Designated Roth plan cash: {order.id}",
        cash_received=row["net_cash"],
        withholding=row["source_withholding"],
        federal=FederalIncome(
            taxable_pension=row["federal_taxable"],
            retirement_additional_tax=row["additional_tax"],
        ),
        new_jersey=NJIncome(
            pension=row["nj_taxable"],
            retirement=RetirementEligibility(
                qualified_pension=row["nj_taxable"] if order.date.year - born.year >= 62 else ZERO,
            ),
        ),
    )
