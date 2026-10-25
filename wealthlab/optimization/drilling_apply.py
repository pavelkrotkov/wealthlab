"""Select one validated complete drilling profile without editing any account or wallet."""

from wealthlab.household.scenario import Scenario
from wealthlab.optimization.drilling_profiles import validate_offers


def apply(data, offers, selected_id, envelope, search_scope):
    """The integrating compiler supplies the original complete scope and valid candidate data."""
    baseline = Scenario.model_validate(search_scope["household"])
    validate_offers(baseline, offers, envelope, search_scope)
    selected = {offer.id: offer for offer in offers}.get(selected_id)
    if selected is None:
        raise ValueError("Select a known complete drilling offer.")
    candidate = Scenario.model_validate(data)
    ensure_capital(candidate, baseline)
    data["drilling_plan"] = selected.plan.model_dump(mode="json") if selected.plan else None


def ensure_capital(candidate, baseline):
    identity = baseline.drilling_plan.account_id
    original = next(account for account in baseline.accounts if account.id == identity)
    current = next((account for account in candidate.accounts if account.id == identity), None)
    if current != original:
        raise ValueError("Drilling selection cannot change its original household account capital.")
