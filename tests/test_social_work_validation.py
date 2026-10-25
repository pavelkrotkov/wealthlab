"""Work histories, observed earnings and unsupported auxiliary profiles fail closed."""

import pytest
from social_work_cases import calculate, payload

from wealthlab.retirement.social_work_case import SocialWorkCase


@pytest.mark.parametrize(
    "field",
    [
        "complete_current_us_w2_wages_without_special_payments_confirmed",
        "no_prior_unmodeled_work_positions_or_reduction_credits_confirmed",
        "no_auxiliary_work_effects_in_this_profile_confirmed",
        "administrative_payment_timing_and_recovery_are_conditional_confirmed",
        "no_special_lump_sum_tax_election_assumed",
    ],
)
def test_every_required_scope_confirmation_is_enforced(field):
    data = payload()
    data["work"][field] = False
    with pytest.raises(ValueError, match="Confirm"):
        SocialWorkCase.model_validate(data)


@pytest.mark.parametrize(
    "change,match",
    [
        ("missing", "complete work report"),
        ("duplicate", "complete work report"),
        ("id", "IDs must be unique"),
        ("actual", "realized monthly"),
        ("unresolved", "Resolve work report"),
        ("grace", "prior grace-year"),
        ("death", "dated-deaths survival policy"),
    ],
)
def test_incomplete_or_unsupported_work_history_cannot_be_projected(change, match):
    data = payload()
    years = data["work"]["years"]
    edits = {
        "missing": lambda: years.pop(),
        "duplicate": lambda: years.append(dict(years[0])),
        "id": lambda: years[1].update(id=years[0]["id"]),
        "actual": lambda: years[0].update(actual_monthly_wages=None),
        "unresolved": lambda: years[0].update(provenance="unresolved"),
        "grace": lambda: data["work"].update(grace_used_before_projection={}),
        "death": lambda: data["claims"]["members"][0].update(
            death_date="2028-05-01", survivor_claim_month="2028-05-01"
        ),
    }
    edits[change]()
    with pytest.raises(ValueError, match=match):
        SocialWorkCase.model_validate(data)


def test_spousal_add_on_cannot_silently_skip_earnings_effects():
    data = payload()
    person = data["claims"]["members"][0]
    person.update(partner="spouse", spousal_eligibility_confirmed=True)
    data["claims"]["members"].append(
        dict(person, id="spouse", partner="worker", pia_january_2026=100)
    )
    data["work"]["grace_used_before_projection"]["spouse"] = False
    data["work"]["years"] += [
        dict(row, id=row["id"] + "-s", member="spouse") for row in list(data["work"]["years"])
    ]
    with pytest.raises(ValueError, match="Auxiliary/survivor work effects"):
        calculate(data)
