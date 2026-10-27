"""Validate complete native source profiles while retaining the original capital and rights."""

from wealthlab.employment.compensation_projection import prepare as prepare_compensation
from wealthlab.employment.wages import prepare as prepare_work
from wealthlab.household.scenario import Scenario


def dates(household):
    return {member.id: member.retirement_date for member in household.members}


def source(record, household):
    if record.provenance == "unresolved" or not record.source.strip():
        raise ValueError("Resolve the source of every employer applicability profile.")
    if not record.source_date <= record.available_on <= household.start:
        raise ValueError("Employer profile sources must be available by the opening decision.")
    if not (
        record.all_candidate_income_and_market_paths_confirmed
        and record.complete_cash_tax_vesting_forfeiture_and_exit_facts_confirmed
    ):
        raise ValueError("Confirm complete employer facts valid across the projected envelope.")


def validate_offer(case, offer):
    source(offer, case.household)
    original = case.household.compensation_plan
    if original is None:
        raise ValueError("Employment offers require the original employer compensation book.")
    if set(offer.retirement_dates) != set(dates(case.household)):
        raise ValueError("Employer profiles must specify every member retirement date exactly.")
    # Events may differ under supplied work choices; original vested/contingent
    # positions, liquidity rights and already compiled tax allocations cannot.
    if original.model_dump(exclude={"events"}) != offer.compensation_plan.model_dump(
        exclude={"events"}
    ):
        raise ValueError("Keep original employer tranches, rights and compiled allocations fixed.")
    validate_work(case.household.employment_plan, offer.employment_plan)
    data = case.household.model_dump(mode="json")
    for member in data["members"]:
        member["retirement_date"] = str(offer.retirement_dates[member["id"]])
    data["employment_plan"] = (
        offer.employment_plan.model_dump(mode="json") if offer.employment_plan else None
    )
    data["compensation_plan"] = offer.compensation_plan.model_dump(mode="json")
    prepare_compensation(prepare_work(Scenario.model_validate(data)))


def validate_work(original, proposed):
    if original is None or proposed is None:
        if original != proposed:
            raise ValueError("Keep the original employment wage-path identities fixed.")
        return
    left = [path.model_dump(exclude={"changes"}) for path in original.paths]
    right = [path.model_dump(exclude={"changes"}) for path in proposed.paths]
    if left != right:
        raise ValueError("Keep employment owners, wage streams and opening pay multipliers fixed.")


def baseline(case, offers):
    for offer in offers.values():
        if (
            offer.retirement_dates == dates(case.household)
            and offer.employment_plan == case.household.employment_plan
            and offer.compensation_plan == case.household.compensation_plan
        ):
            return
    raise ValueError("The original household needs its own complete matching employment profile.")
