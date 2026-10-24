"""Synthetic survivor dates, never an inference about an actual household or SSA award."""

from wealthlab.retirement.social_example import synthetic
from wealthlab.retirement.social_inputs import SocialCase


def switch_case():
    data = synthetic().model_dump(mode="json")
    data.update(start_year=2031, end_year=2037, survival_policy="dated_deaths")
    data["members"][0]["death_date"] = "2031-07-15"
    data["members"][1].update(
        birth_date="1965-01-02",
        pia_january_2026=3000,
        claim_month="2035-01-01",
        survivor_claim_month="2031-07-01",
        survivor_eligibility_confirmed=True,
    )
    return SocialCase.model_validate(data)


def early_limit():
    data = synthetic().model_dump(mode="json")
    data.update(start_year=2026, end_year=2030, survival_policy="dated_deaths")
    data["members"][0].update(
        claim_month="2022-01-01", death_date="2026-01-15", spousal_eligibility_confirmed=False
    )
    data["members"][1].update(
        pia_january_2026=0,
        own_insured=False,
        claim_month="2022-01-01",
        survivor_claim_month="2026-09-01",
        survivor_eligibility_confirmed=True,
    )
    return SocialCase.model_validate(data)
