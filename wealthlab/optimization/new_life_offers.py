"""Select complete supplied new issues without replacing existing household capital.

Owner and independent insurance need are explicit; a birth date cannot identify
an owner. Quotes are indivisible supplied paths, not premium-scaled valuations.
All offers, including inactive alternatives, must pass native path validation.
"""

from wealthlab.household.scenario import Scenario
from wealthlab.optimization.new_life_inputs import NewLifeOffer as NewLifeOffer
from wealthlab.products.life_contract_tax import TERMINAL
from wealthlab.products.life_household_validation import validate as validate_native


def validate_offers(household, offers):
    if len({offer.id for offer in offers}) != len(offers):
        raise ValueError("New-life offer identifiers must be unique.")
    if not offers:
        return
    if household.life_plan is None:
        raise ValueError("New-life offers require an explicit baseline insurance-need plan.")
    for offer in offers:
        validate_offer(household, offer)


def validate_offer(household, offer):
    if (
        offer.provenance == "unresolved"
        or not offer.matched_new_issue_terms_confirmed
        or not offer.source.strip()
    ):
        raise ValueError("Confirm the complete independently sourced new-issue terms.")
    if offer.owner not in household.life_plan.insurance_need_by_owner:
        raise ValueError("Retain a supplied independent baseline need for the offered owner.")
    if offer.holding.account_id in {account.id for account in household.accounts}:
        raise ValueError("A new-life offer cannot replace any existing account or policy.")
    validate_opening(household, offer.holding)
    validate_schedule(household, offer.holding.contract)
    trial = household.model_dump(mode="json")
    _inject(trial, offer)
    validate_native(Scenario.model_validate(trial))


def zero_values(value):
    return (value.gross_cash_value, value.gross_surrender_value, value.gross_death_benefit) == (
        0,
        0,
        0,
    )


def validate_opening(household, holding):
    contract = holding.contract
    if contract.source_date > household.start:
        raise ValueError("New-issue quote source must be available at household start.")
    if not zero_values(holding.opening_values) or (
        contract.opening_federal_basis,
        contract.opening_loan,
    ) != (0, 0):
        raise ValueError("New issues require zero opening values, coverage, known basis and loan.")
    if (
        contract.start != household.start
        or contract.issue_date != household.start
        or holding.opening_values.date != household.start
    ):
        raise ValueError("New-issue opening and issue dates must match the household start.")


def validate_schedule(household, contract):
    events = contract.events
    if not events or events[0].kind != "premium" or events[0].amount <= 0:
        raise ValueError("A new issue must start with an actual positive premium event.")
    if events[-1].kind not in TERMINAL or events[-1].date >= household.end:
        raise ValueError("Supply a full new-policy terminal exit inside the household horizon.")
    validate_prefunding_values(contract)


def validate_prefunding_values(contract):
    first = contract.events[0].date
    if any(not zero_values(v) for v in contract.values if v.date < first):
        raise ValueError("New-policy values and coverage must stay zero before the first premium.")


def selected_offers(offers, selected_ids):
    known = {offer.id: offer for offer in offers}
    if len(set(selected_ids)) != len(selected_ids) or set(selected_ids) - known.keys():
        raise ValueError("Select unique known new-life offer identifiers.")
    selected = [known[identity] for identity in selected_ids]
    if len({offer.holding.account_id for offer in selected}) != len(selected):
        raise ValueError("Alternative new-life illustrations sharing a destination are exclusive.")
    return selected


def _inject(data, offer):
    data["accounts"].append(
        dict(
            id=offer.holding.account_id,
            provenance=offer.provenance,
            owner=offer.owner,
            currency="USD",
            wrapper="insurance",
            balance="0",
            monthly_fee="0",
        )
    )
    data["life_plan"]["holdings"].append(offer.holding.model_dump(mode="json"))


def apply(data, offers, selected_ids):
    """Validate inactive offers and selection before mutating raw compiler JSON inputs."""
    validate_offers(Scenario.model_validate(data), offers)
    selected = selected_offers(offers, selected_ids)
    for offer in selected:
        _inject(data, offer)
