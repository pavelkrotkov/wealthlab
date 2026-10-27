"""Malformed tier/calendar contracts and unavailable native value bases fail before projection."""

import pytest

from tests.advisory_cases import change, plain, with_fee
from wealthlab.household.projection import project


@pytest.mark.parametrize(
    "tiers",
    [
        [dict(upper_limit="100000", annual_rate=".01")],
        [dict(upper_limit=None, annual_rate=".01"), dict(upper_limit=None, annual_rate=".01")],
        [dict(upper_limit="0", annual_rate=".01"), dict(upper_limit=None, annual_rate=".01")],
        [
            dict(upper_limit="100", annual_rate=".01"),
            dict(upper_limit="50", annual_rate=".01"),
            dict(upper_limit=None, annual_rate=".01"),
        ],
    ],
)
def test_marginal_tiers_are_complete_ordered_and_have_an_explicit_unlimited_last_band(tiers):
    with pytest.raises(ValueError, match=r"marginal AUM|Marginal AUM"):
        project(change(with_fee(plain()), lambda p: p["schedules"][0].update(tiers=tiers)))


def test_duplicate_or_overlapping_periods_cannot_charge_the_same_accrual_twice():
    with pytest.raises(ValueError, match="overlap or repeat"):
        project(
            change(
                with_fee(plain()),
                lambda p: p["schedules"][0].update(periods=p["schedules"][0]["periods"] * 2),
            )
        )


def test_unavailable_life_or_wrapper_bases_do_not_use_a_default_zero_or_stale_mark():
    case = with_fee(plain())

    def wrong_life(p):
        p["schedules"][0]["covered"][0].update(value_basis="life_net_cash_value")

    with pytest.raises(ValueError, match="native insurance account"):
        project(change(case, wrong_life))
    account = case.accounts[1].model_copy(update=dict(wrapper="education"))
    with pytest.raises(ValueError, match="lacks the selected net basis"):
        project(case.model_copy(update=dict(accounts=[case.accounts[0], account])))
