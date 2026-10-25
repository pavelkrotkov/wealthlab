"""Finite allowed choices are the bounds; a lock selects exactly one named choice."""

from datetime import date
from decimal import Decimal

from pydantic import Field

from wealthlab.household.records import Identifier
from wealthlab.household.scenario import Scenario
from wealthlab.markets.guardrail_inputs import SpendingGuardrail
from wealthlab.markets.household_inputs import HouseholdBinding
from wealthlab.markets.inputs import MarketCase
from wealthlab.optimization.account_controls import AccountControls
from wealthlab.optimization.robustness_inputs import RobustnessCheck
from wealthlab.portfolio.harvest_policy import HarvestPolicy
from wealthlab.portfolio.policies import SalePolicy
from wealthlab.portfolio.rebalance_inputs import RebalancePolicy
from wealthlab.portfolio.saving_inputs import SavingPolicy
from wealthlab.retirement.distribution_inputs import WithdrawalOrder
from wealthlab.tax.facts import TaxModel


class PolicyChoice(AccountControls):
    """One atomic allowed proposal; None preserves a schedule, [] deliberately clears it.

    IRA orders reuse dated withdrawal/conversion and tax-basis rules. Funding
    order contains only indices of existing permitted sources, never new assets.
    A guardrail needs a separate change flag so clearing it is distinguishable
    from leaving the shared baseline unchanged. No choice can edit spending,
    opening capital, tax eligibility, fees or expected market returns.
    """

    id: Identifier
    retirement_dates: dict[Identifier, date] = Field(default_factory=dict)
    sale_policies: list[SalePolicy] | None = None
    harvest_policies: list[HarvestPolicy] | None = None
    rebalances: list[RebalancePolicy] | None = None
    savings: list[SavingPolicy] | None = None
    ira_orders: list[WithdrawalOrder] | None = None
    lot_funding_order: list[int] | None = None
    change_guardrail: bool = False
    guardrail: SpendingGuardrail | None = None


class Dimension(TaxModel):
    """An explicit user menu, with an optional lock to one of its named choices."""

    id: Identifier
    choices: list[PolicyChoice] = Field(min_length=1, max_length=32)
    locked_choice: Identifier | None = None


class SearchTargets(TaxModel):
    """Point-estimate targets remain separate from sampling confidence intervals."""

    success_fraction: float = Field(default=0.95, gt=0, le=1)
    reserve_years: float = Field(default=2, ge=0, le=20)
    target_age: int = Field(default=100, ge=50, le=120)
    maximum_issuer_weight: Decimal | None = Field(default=Decimal(1), ge=0, le=1)


class PolicySearch(TaxModel):
    """A common household and market model with independently seeded validation."""

    household: Scenario
    binding: HouseholdBinding
    training: MarketCase
    validation: MarketCase
    robustness: dict[Identifier, RobustnessCheck] = Field(default_factory=dict, max_length=12)
    dimensions: list[Dimension] = Field(min_length=1, max_length=8)
    targets: SearchTargets = Field(default_factory=SearchTargets)
    maximum_candidates: int = Field(default=128, ge=1, le=512)
    maximum_projection_months: int = Field(default=100000, ge=1, le=1000000)
