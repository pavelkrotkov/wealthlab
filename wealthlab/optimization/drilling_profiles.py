"""Whole supplied allocation profiles remain opaque; no proportional tax/cash facts are invented."""

from wealthlab.household.scenario import Scenario
from wealthlab.optimization.drilling_scope import validate_envelope, validate_releases
from wealthlab.optimization.drilling_terms import (
    validate_decline,
    validate_fixed,
    validate_mode_change,
)
from wealthlab.products.drilling_accounts import validate_account
from wealthlab.products.drilling_validation import validate as validate_native


def validate_offers(household, offers, envelope, search_scope):
    if household.drilling_plan is None or household.tax_plan is None:
        raise ValueError("Drilling offers require an original native drilling account and plan.")
    validate_envelope(household, envelope, search_scope)
    validate_account(household, household.drilling_plan)
    if len({o.id for o in offers}) != len(offers):
        raise ValueError("Drilling offer identifiers must be unique.")
    for offer in offers:
        validate_offer(household, offer, envelope)


def validate_offer(household, offer, envelope):
    if (
        offer.provenance == "unresolved"
        or not offer.source.strip()
        or not offer.complete_matched_terms_confirmed
        or offer.source_date > household.start
    ):
        raise ValueError("Every drilling offer needs complete known-at-opening independent terms.")
    baseline = household.drilling_plan
    if offer.plan is None:
        validate_decline(baseline, offer)
        return
    if offer.declined_no_prior_interest_or_obligations_confirmed:
        raise ValueError("A supplied drilling interest cannot also be a declined no-entry offer.")
    validate_mode_change(baseline, offer)
    validate_fixed(baseline, offer.plan)
    validate_releases(offer.plan, envelope)
    trial = household.model_dump(mode="json")
    trial["drilling_plan"] = offer.plan.model_dump(mode="json")
    validate_native(Scenario.model_validate(trial))
