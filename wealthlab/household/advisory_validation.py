"""Only complete sourced contracts reach the shared observed-value assessment book.

Rate methods are supplied contract inputs, not a guessed blended rate. Independent
source and availability dates prevent a later fee quote from changing an earlier
cash decision. Embedded product costs must be excluded from this outer bill.
"""

from wealthlab.household.advisory_billing import validate as validate_billing
from wealthlab.household.advisory_calendar import validate_periods
from wealthlab.household.advisory_scope import validate_coverage


def validate(scenario):
    plan = scenario.advisory_fee_plan
    cash = [a.id for a in scenario.accounts if a.wrapper == "cash"]
    if plan.payment_account_ids != cash:
        raise ValueError("Advisory payment IDs must exactly match the ordered household cash pool.")
    ids = [s.id for s in plan.schedules]
    if len(ids) != len(set(ids)):
        raise ValueError("Advisory schedule IDs must be unique.")
    for schedule in plan.schedules:
        validate_source(schedule)
        validate_billing(schedule)
        validate_tiers(schedule.tiers)
        validate_periods(scenario, schedule)
        validate_coverage(scenario, schedule)


def validate_source(schedule):
    if schedule.provenance == "unresolved" or not schedule.source_ref.strip():
        raise ValueError("Advisory terms need a resolved nonempty source reference.")
    if not (
        schedule.contract_terms_and_valuation_basis_confirmed
        and schedule.outer_cash_fee_not_already_in_embedded_costs_confirmed
    ):
        raise ValueError("Confirm advisory terms/basis and separate outer versus embedded costs.")
    if (
        not schedule.source_date
        <= schedule.available_on
        <= min(schedule.periods[0].accrual_start, schedule.periods[0].assessment_date)
    ):
        raise ValueError("Advisory source and availability must precede the first accrual period.")


def validate_tiers(tiers):
    previous = 0
    for tier in tiers[:-1]:
        if tier.upper_limit is None or tier.upper_limit <= previous:
            raise ValueError(
                "Marginal AUM tiers / whole-base limits must be finite and strictly increasing."
            )
        previous = tier.upper_limit
    if tiers[-1].upper_limit is not None:
        raise ValueError(
            "The last marginal AUM tier / whole-base breakpoint must have no upper limit."
        )
