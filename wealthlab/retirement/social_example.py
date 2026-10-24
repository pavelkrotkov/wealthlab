"""Synthetic delayed claims expose the spouse offset against own delayed retirement credits."""

from wealthlab.retirement.social_inputs import SocialCase


def synthetic():
    common = dict(
        provenance="illustration",
        birth_date="1960-01-02",
        own_insured=True,
        claim_month="2030-01-01",
        spousal_eligibility_confirmed=True,
    )
    return SocialCase.model_validate(
        dict(
            start_year=2030,
            end_year=2033,
            no_earnings_test_deductions_confirmed=True,
            no_other_auxiliaries_confirmed=True,
            history_policy="no_prior_deductions_suspensions_disability_or_restricted_claims",
            claim_rule_policy="freeze_current_claim_rules",
            survival_policy="all_members_survive_projection",
            future_cola_assumption=0,
            payment_policy="following_month_no_offsets",
            members=[
                dict(id="person", pia_january_2026=2500, partner="spouse", **common),
                dict(id="spouse", pia_january_2026=1000, partner="person", **common),
            ],
        )
    )
