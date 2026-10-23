"""NJ-specific annual recognized income and explicitly qualified deductions."""

from decimal import Decimal

from pydantic import Field

from wealthlab.household.records import Money
from wealthlab.tax.facts import SignedMoney, TaxModel
from wealthlab.tax.nj_business import BusinessIncome
from wealthlab.tax.nj_retirement import RetirementEligibility


class NJIncome(TaxModel):
    wages: Money = Decimal(0)
    interest: Money = Decimal(0)
    dividends: Money = Decimal(0)
    dispositions: SignedMoney = Decimal(0)
    pension: Money = Decimal(0)
    other: Money = Decimal(0)
    business: BusinessIncome = Field(default_factory=BusinessIncome)
    retirement: RetirementEligibility = Field(default_factory=RetirementEligibility)


class NJDeductions(TaxModel):
    medical: Money = Decimal(0)
    qualified_msa: Money = Decimal(0)
    self_employed_health: Money = Decimal(0)
    alimony: Money = Decimal(0)
    conservation: Money = Decimal(0)
    health_enterprise_zone: Money = Decimal(0)
    organ_donation: Money = Decimal(0)
    njbest: Money = Decimal(0)
    njclass: Money = Decimal(0)
    nj_tuition: Money = Decimal(0)
    # Already allocated to this return's ownership/residency share, including
    # 18% of qualifying rent and any applicable Senior Freeze base-year limit.
    qualifying_property_tax: Money = Decimal(0)
    property_eligible: bool = False
    separate_same_home: bool = False
    blind_disabled_adults: int = Field(default=0, ge=0, le=2)
    veteran_adults: int = Field(default=0, ge=0, le=2)
    qualifying_college_dependents: int = Field(default=0, ge=0)
