"""NJ-BUS-2 adjustment and dated business-loss carry; not a capital-loss ledger."""

from decimal import Decimal

from pydantic import Field

from wealthlab.household.records import Money
from wealthlab.tax.facts import SignedMoney, TaxModel


class BusinessLoss(TaxModel):
    year: int = Field(ge=2012, le=2145)
    amount: Money


class BusinessIncome(TaxModel):
    business: SignedMoney = Decimal(0)
    partnership: SignedMoney = Decimal(0)
    s_corporation: SignedMoney = Decimal(0)
    rents: SignedMoney = Decimal(0)
    carry: list[BusinessLoss] = Field(default_factory=list)


def adjustment(income: BusinessIncome, year: int) -> dict:
    """NJ-BUS-2 lines 6-12, with expiry and oldest-first carry consumption.

    Each category is already netted under NJ-BUS-1 using NJ basis. Disposition
    losses and federal passive/capital carryforwards never enter this input.
    """
    validate(income, year)
    values = [income.business, income.partnership, income.s_corporation, income.rents]
    regular = sum((max(Decimal(0), item) for item in values), Decimal(0))
    net = sum(values, Decimal(0))
    live = sorted((item for item in income.carry if year - item.year <= 20), key=lambda x: x.year)
    prior = sum((item.amount for item in live), Decimal(0))
    remaining = consume(live, max(Decimal(0), net))
    if net < 0:
        remaining.append(BusinessLoss(year=year, amount=-net))
    return dict(
        regular_income=regular,
        adjustment=(regular - max(Decimal(0), net - prior)) / 2,
        carry=remaining,
        expired=sum((item.amount for item in income.carry if year - item.year > 20), Decimal(0)),
    )


def consume(carry: list[BusinessLoss], income: Decimal) -> list[BusinessLoss]:
    remaining = []
    for item in carry:
        used = min(income, item.amount)
        income -= used
        if item.amount > used:
            remaining.append(BusinessLoss(year=item.year, amount=item.amount - used))
    return remaining


def validate(income: BusinessIncome, year: int) -> None:
    if any(item.year >= year for item in income.carry):
        raise ValueError("Business carry must originate before the tax year.")
    if len({item.year for item in income.carry}) != len(income.carry):
        raise ValueError("Combine business losses with the same origin year.")
