"""Missing alternate PIA, death dates or legal eligibility cannot silently create an award."""

import pytest

from tests.test_survivor_cash import calculate, payload


@pytest.mark.parametrize(
    ("field", "value"), [("death_date", "1959-01-01"), ("survivor_pia_january_2026", "1000.01")]
)
def test_invalid_deceased_inputs_fail(field, value):
    data = payload()
    data["members"][0][field] = value
    with pytest.raises(ValueError):
        calculate(data)


@pytest.mark.parametrize("claim", ["2031-06-01", "2020-01-01", "2031-07-02"])
def test_survivor_claim_cannot_precede_death_or_age60_or_use_a_partial_month(claim):
    data = payload()
    data["members"][1]["survivor_claim_month"] = claim
    with pytest.raises(ValueError, match="eligible first-of-month"):
        calculate(data)


def test_survival_policy_cannot_ignore_an_included_death():
    data = payload()
    data["survival_policy"] = "all_members_survive_projection"
    with pytest.raises(ValueError, match="dated-deaths"):
        calculate(data)


def test_claim_needs_a_dated_partner_death_and_a_living_claimant():
    data = payload()
    data["members"][0]["death_date"] = None
    with pytest.raises(ValueError, match="known partner and dated death"):
        calculate(data)
    data = payload()
    data["members"][1]["death_date"] = "2031-07-15"
    with pytest.raises(ValueError, match="own death month"):
        calculate(data)
