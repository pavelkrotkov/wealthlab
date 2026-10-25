"""A sourced subscription profile changes decisions, not opening wealth or favorable tax law.

The native books derive actual gains, eligible amounts, dates, basis and cash.
No supplied K1 or legal fact is proportionally scaled by this adapter.
"""

from wealthlab.employment.compensation_projection import prepare as prepare_compensation
from wealthlab.employment.wages import prepare as prepare_employment
from wealthlab.household.scenario import Scenario
from wealthlab.portfolio.household_book import make as make_lots
from wealthlab.products.qoz_household import Ledger
from wealthlab.retirement.social_household import prepare_with_work
from wealthlab.tax.projection_ledger import TaxLedger

VARIABLE = {"calls", "sale_requested", "mode"}
CALL_VARIABLE = {"date", "amount", "recapitalization_units"}


def validate_native(household):
    if household.tax_plan is None:
        raise ValueError("QOZ policy search requires an explicit native household tax plan.")
    prepared, _ = prepare_with_work(prepare_compensation(prepare_employment(household)))
    lots = make_lots(prepared)
    tax = TaxLedger(prepared.tax_plan, prepared, lots)
    Ledger(prepared, lots, tax)


def validate_offer(household, offer):
    if offer.provenance == "unresolved" or not offer.source.strip():
        raise ValueError("Provide a resolved source for each complete QOZ offer.")
    if not (
        offer.complete_cash_tax_and_terms_confirmed
        and offer.profile_valid_for_all_candidate_income_and_paths_confirmed
    ):
        raise ValueError("Confirm complete QOZ terms valid for every candidate and price path.")
    if offer.source_date > household.start:
        raise ValueError("QOZ offer sources must be available at the opening decision.")
    if offer.plan is None:
        validate_decline(household, offer)
        return
    if offer.declined_no_prior_interest_or_obligations_confirmed:
        raise ValueError("An active QOZ subscription cannot also be a no-entry offer.")
    validate_shared(household.qoz_plan, offer.plan)
    data = household.model_dump(mode="json")
    data["qoz_plan"] = offer.plan.model_dump(mode="json")
    validate_native(Scenario.model_validate(data))


def validate_decline(household, offer):
    if not offer.declined_no_prior_interest_or_obligations_confirmed:
        raise ValueError("Confirm no prior QOZ interest or obligations when declining entry.")
    # The native profile separately proves zero opening value and optional future calls.
    validate_native(household)


def validate_shared(original, proposed):
    if original.model_dump(exclude=VARIABLE) != fixed_profile(proposed, original):
        raise ValueError(
            "Keep QOZ eligibility, fees, lockups, settlement and original capital fixed."
        )
    left = {c.id: c.model_dump(exclude=CALL_VARIABLE) for c in original.calls}
    right = {c.id: c.model_dump(exclude=CALL_VARIABLE) for c in proposed.calls}
    if left != right or len(right) != len(proposed.calls):
        raise ValueError(
            "Preserve original QOZ call identities, source lots and issuance assumptions."
        )


def fixed_profile(proposed, original):
    if proposed.mode == "liquid_reference":
        if (proposed.federal, proposed.new_jersey, proposed.settlement_months) != (
            "denied",
            "denied",
            0,
        ):
            raise ValueError(
                "Liquid QOZ references require denied tax elections and immediate settlement."
            )
        proposed = proposed.model_copy(
            update=dict(
                federal=original.federal,
                new_jersey=original.new_jersey,
                settlement_months=original.settlement_months,
            )
        )
    return proposed.model_dump(exclude=VARIABLE)


def preserve_account(data, household):
    # Reject a malformed candidate before changing its original ownership or capital.
    candidate = Scenario.model_validate(data)
    account_id = household.qoz_plan.account_id
    original = next(a for a in household.accounts if a.id == account_id)
    if next((a for a in candidate.accounts if a.id == account_id), None) != original:
        raise ValueError("QOZ participation must preserve its original household account.")
