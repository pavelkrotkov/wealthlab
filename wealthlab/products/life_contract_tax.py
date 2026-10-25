"""Section72 ordinary personal-contract profile, with unknowns propagated.

Opening investment includes prior taxed-loan adjustments supplied by the owner.
This is not a premium-total reconstruction. An unconfirmed distribution makes
subsequent investment unknown; later premiums cannot repair missing history.
"""

from decimal import Decimal

from wealthlab.household.calendar import money
from wealthlab.retirement.roth_reconciliation import half_birthday

ZERO = Decimal(0)
RECEIPTS = {"withdrawal", "dividend_cash"}
LOANS = {"loan_advance", "capitalized_interest"}
TERMINAL = {"surrender", "lapse"}


def known(contract):
    return (
        contract.ordinary_personal_contract_confirmed
        and contract.no_aggregation_or_special_basis_adjustments_confirmed
        and contract.federal_status != "unknown"
    )


def distribution(contract, event, basis):
    if basis is None or not known(contract):
        return None, None
    if event.kind in TERMINAL:
        return max(ZERO, event.amount - basis), ZERO
    if contract.federal_status == "non_mec":
        return ordinary(contract, event, basis)
    from wealthlab.products.life_contract_mec import recognize as mec

    return mec(contract, event, basis)


def ordinary(contract, event, basis):
    if event.kind in LOANS:
        return ZERO, basis
    if not contract.withdrawals_without_early_benefit_recapture_confirmed:
        return None, None
    taxable = max(ZERO, event.amount - basis)
    return taxable, max(ZERO, basis - event.amount)


def recognize(contract, event, basis):
    if not known(contract):
        return None, None
    if event.kind in RECEIPTS | LOANS | TERMINAL:
        return distribution(contract, event, basis)
    if event.kind == "premium" and basis is not None:
        basis += event.amount
    return ZERO, basis


def additional(contract, event, taxable):
    if taxable is None:
        return None
    exempt = contract.additional_tax_exception != "none"
    older = event.date >= half_birthday(contract.owner_birth_date)
    if contract.federal_status != "mec" or exempt or older:
        return ZERO
    return money(taxable * Decimal("0.10"))
