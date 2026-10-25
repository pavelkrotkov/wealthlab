"""Validate each entry point before applying the inside-HSA investment profile.

The generic lot engine rejects HSA accounts. This profile reuses its cash and
basis arithmetic with ordinary federal investment exemption and explicitly
conditional NJ recognition. It never infers IRA wash treatment for an HSA or
mixes outside taxable purchases into an unverified state classification.
"""

from wealthlab.portfolio.validation import validate as validate_lots
from wealthlab.retirement.hsa_investment_events import (
    validate_events,
    validate_prices,
    validate_sources,
)


def validate(plan):
    case = plan.case
    if not all(
        (
            plan.complete_positions_and_state_basis_confirmed,
            plan.conditional_state_treatment_confirmed,
            plan.no_identical_outside_trading_confirmed,
            plan.fees_are_custodian_charges_confirmed,
            plan.ordinary_securities_no_ubti_confirmed,
        )
    ):
        raise ValueError(
            "Confirm HSA positions, NJ basis/tax assumptions, outside trades, fees and no UBTI."
        )
    validate_scope(case)
    if any(f.treatment == "cash" and f.kind != "custody" for f in case.fee_schedules):
        raise ValueError("Cash HSA fees must be explicitly confirmed custodian charges.")
    validate_lots(case, hsa_investment=True)
    validate_prices(plan)
    validate_sources(plan)
    validate_events(plan)
    validate_entry_ids(plan)


def validate_scope(case):
    for account in case.accounts:
        validate_account(account)
    if case.federal_wash_tracking or case.nj_wash_treatment != "no_wash_assumption":
        raise ValueError("HSA investments require explicit separate no-wash state assumptions.")
    if any(
        (
            case.sale_policies,
            case.harvest_policies,
            case.compare_harvesting,
            case.terminal_exit,
            case.lot_tax_cases,
        )
    ):
        raise ValueError(
            "Use actual HSA trades/cash targets; taxable-account tax policies cannot apply."
        )
    if any(s.kind == "collectible" for s in case.securities):
        raise ValueError("Collectibles need a separately validated HSA eligibility/product model.")


def validate_entry_ids(plan):
    records = [*plan.cash_targets, *plan.liquidity_locks]
    ids = [r.id for r in records]
    occupied = {
        r.id
        for r in [
            *plan.case.lots,
            *plan.case.trades,
            *plan.case.distributions,
            *plan.case.fee_schedules,
        ]
    }
    if len(ids) != len(set(ids)) or set(ids) & occupied:
        raise ValueError(
            "HSA target/lock IDs must be distinct from each other and existing events."
        )


def validate_account(account):
    if account.wrapper != "hsa":
        raise ValueError("The dedicated HSA investment book accepts HSA accounts only.")
    if account.owner == "joint":
        raise ValueError("HSA investment accounts require individual ownership.")
