"""Synthetic POMS partial-month arithmetic plus a dated future ARF cash assumption."""

from wealthlab.retirement.social_work_case import SocialWorkCase


def synthetic():
    return SocialWorkCase.model_validate(
        dict(
            claims=dict(
                start_year=2026,
                end_year=2033,
                no_earnings_test_deductions_confirmed=True,
                no_other_auxiliaries_confirmed=True,
                history_policy="no_prior_deductions_suspensions_disability_or_restricted_claims",
                claim_rule_policy="freeze_current_claim_rules",
                survival_policy="all_members_survive_projection",
                future_cola_assumption=0,
                payment_policy="following_month_no_offsets",
                members=[
                    dict(
                        id="worker",
                        provenance="illustration",
                        birth_date="1964-01-02",
                        pia_january_2026=803,
                        own_insured=True,
                        claim_month="2026-01-01",
                        partner=None,
                        spousal_eligibility_confirmed=False,
                    )
                ],
            ),
            work=dict(
                rule_mode="frozen_2026_us_w2_annual_and_monthly_tests",
                grace_used_before_projection={"worker": False},
                closed_year_payment_month=5,
                arf_payment_month_following_fra_year=5,
                overpayment_recovery_fraction=1,
                complete_current_us_w2_wages_without_special_payments_confirmed=True,
                no_prior_unmodeled_work_positions_or_reduction_credits_confirmed=True,
                no_auxiliary_work_effects_in_this_profile_confirmed=True,
                administrative_payment_timing_and_recovery_are_conditional_confirmed=True,
                no_special_lump_sum_tax_election_assumed=True,
                years=[
                    dict(
                        id=f"work-{year}",
                        provenance="illustration",
                        member="worker",
                        year=year,
                        forecast_monthly_wages=wages(year),
                        actual_monthly_wages=wages(year),
                    )
                    for year in range(2026, 2033)
                ],
            ),
        )
    )


def wages(year):
    return [3842] + [2400] * 11 if year == 2026 else [0] * 12
