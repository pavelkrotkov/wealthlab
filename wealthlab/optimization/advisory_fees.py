"""Common sourced fee terms follow actual candidates; new strategy accounts need explicit scope.

A zero allocation cannot erase the common contract. Conditional account coverage
must be supplied before any offer, including a locked/inactive one, is selected.
Native execution creates each bill from its actual observed values, not unit-scaled
or precomputed AUM. A sourced zero-rate schedule is a fact, never a choice field.
"""

from wealthlab.household.advisory_validation import validate as validate_native

EQUITY = {"modeled_net_account_equity"}
LIFE = {"life_net_cash_value", "life_net_surrender_value"}


def validate(case):
    plan = case.household.advisory_fee_plan
    if plan is None:
        return
    validate_native(case.household)
    accounts = {a.id for a in case.household.accounts}
    covered = [c for schedule in plan.schedules for c in schedule.covered]
    for account_id, bases in offered_accounts(case):
        validate_offer(account_id, bases, accounts, covered)


def offered_accounts(case):
    for offer in case.sleeve_opportunities:
        yield offer.unit.account_id, EQUITY
    for offer in [*case.life_opportunities, *case.new_life_opportunities]:
        yield offer.holding.account_id, LIFE
    for path in case.exchange_opportunities:
        yield path.plan.account_id, EQUITY
    yield from declared_product_accounts(case)
    if case.option_opportunity is not None:
        yield case.option_opportunity.unit.account_id, EQUITY


def validate_offer(account_id, bases, accounts, covered):
    entries = [row for row in covered if row.account_id == account_id]
    if not entries:
        raise ValueError(
            "Common sourced advisory coverage must explicitly name every strategy offer."
        )
    for row in entries:
        if row.value_basis not in bases:
            raise ValueError(
                "Every advisory strategy offer needs its supported native value basis."
            )
        if account_id not in accounts and row.presence != "if_present":
            raise ValueError(
                "New strategy advisory accounts require source-confirmed if_present coverage."
            )


def preserved(original, candidate):
    if candidate.advisory_fee_plan != original.advisory_fee_plan:
        raise ValueError(
            "Keep the common sourced advisory contract identical across all candidates."
        )


def cleared(household, row):
    if row.get("fees_owed", 0) != 0:
        return False
    plan = household.advisory_fee_plan
    if plan is None:
        return True
    audit = row.get("advisory_fee_audit")
    return (
        audit is not None
        and row.get("advisory_fees_owed") == 0
        and audit.get("remaining_owed") == 0
        and audit.get("inputs") == plan.model_dump(mode="json")
    )


def declared_product_accounts(case):
    """Declined products can retain present zero accounts; do not infer their absence."""
    for field in ("drilling_offers", "qoz_offers"):
        for offer in getattr(case, field, ()):
            if offer.plan is not None:
                yield offer.plan.account_id, EQUITY
