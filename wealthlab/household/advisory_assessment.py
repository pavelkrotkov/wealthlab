"""All simultaneous advisory bills share observed values; progressive tiers apply marginally."""

from decimal import Decimal

from wealthlab.household.calendar import money

ZERO = Decimal(0)


def component(covered, balances, life_values):
    if covered.account_id not in balances:
        return dict(
            account_id=covered.account_id,
            basis=covered.value_basis,
            status="source_confirmed_absent",
            value=ZERO,
        )
    if covered.value_basis == "modeled_net_account_equity":
        value = balances[covered.account_id]
    else:
        values = next((v for v in life_values if v["account_id"] == covered.account_id), None)
        if values is None:
            raise ValueError("Current native life advisory valuation is unavailable.")
        value = values[covered.value_basis.removeprefix("life_")]
    if value < 0:
        raise ValueError("Advisory net-equity bases cannot invent gross or borrowed asset value.")
    return dict(
        account_id=covered.account_id, basis=covered.value_basis, status="observed", value=value
    )


def marginal_charge(base, tiers):
    # A marginal threshold changes only the next band, never the rate applied
    # to the entire account. Retain each band for independent bill verification.
    lower, charges = ZERO, []
    for tier in tiers:
        upper = base if tier.upper_limit is None else min(base, tier.upper_limit)
        amount = max(ZERO, upper - lower)
        charges.append(
            dict(lower=lower, upper=tier.upper_limit, base=amount, rate=tier.annual_rate)
        )
        if tier.upper_limit is not None:
            lower = tier.upper_limit
    return sum((c["base"] * c["rate"] for c in charges), ZERO), charges


def assess(schedule, period, balances, life_values):
    components = [component(c, balances, life_values) for c in schedule.covered]
    base = sum((c["value"] for c in components), ZERO)
    annual, tiers = marginal_charge(base, schedule.tiers)
    days = (period.accrual_end - period.accrual_start).days
    # Round the complete variable bill once, then add the sourced fixed charge.
    charge = money(annual * days / schedule.day_count) + schedule.fixed_per_period
    return dict(
        schedule=schedule.id,
        source_ref=schedule.source_ref,
        source_date=schedule.source_date.isoformat(),
        available_on=schedule.available_on.isoformat(),
        date=period.assessment_date.isoformat(),
        accrual_start=period.accrual_start.isoformat(),
        accrual_end_exclusive=period.accrual_end.isoformat(),
        valuation_date=period.valuation_date.isoformat(),
        payment_due_date=period.payment_due_date.isoformat(),
        period_days=days,
        day_count=schedule.day_count,
        valuation_base=base,
        components=components,
        marginal_tiers=tiers,
        fixed_charge=schedule.fixed_per_period,
        assessed=charge,
    )
