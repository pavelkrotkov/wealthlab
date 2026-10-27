"""New cash interests use the actual realization holding period, including deferred losses.

A2026-01-01cash acquisition has short-term character through2027-01-01and
long-term character from2027-01-02under the explicitly confirmed ordinary
profile. Existing undated interests retain their supplied conditional character.
"""

from datetime import date
from decimal import Decimal

import pytest

from wealthlab.products.private_fund_character import character
from wealthlab.products.private_fund_example import contract
from wealthlab.products.private_fund_inputs import PrivateFundContract
from wealthlab.products.private_fund_tax import BasisBook


def dated():
    return PrivateFundContract.model_validate(
        dict(
            contract(),
            federal_capital_character=None,
            federal_holding_start="2026-01-01",
            ordinary_holding_period_assumed_confirmed=True,
        )
    )


@pytest.mark.parametrize(
    "when,expected",
    [
        (date(2026, 12, 31), "short_term"),
        (date(2027, 1, 1), "short_term"),
        (date(2027, 1, 2), "long_term"),
    ],
)
def test_cash_realization_uses_more_than_one_calendar_year(when, expected):
    book = BasisBook(dated(), "fund")
    events = book.distribute(Decimal(110000), True, when)
    assert getattr(events[0].federal, expected) == 10000
    other = "short_term" if expected == "long_term" else "long_term"
    assert getattr(events[0].federal, other) == 0


def test_deferred_early_loss_stays_short_term_after_release_in_later_year():
    data = dated().model_dump(mode="json")
    data["federal_exit_loss"] = dict(
        treatment="deferred", release_on="2028-01-01", eligibility_after_limits_assumed=True
    )
    book = BasisBook(PrivateFundContract.model_validate(data), "fund")
    events = book.distribute(Decimal(90000), True, date(2026, 12, 31))
    federal = next(event for event in events if event.federal.short_term)
    assert federal.date == date(2028, 1, 1)
    assert federal.federal.short_term == -10000 and federal.federal.long_term == 0


@pytest.mark.parametrize(
    "changes,match",
    [
        ({"federal_capital_character": "long_term"}, "either a holding start"),
        ({"federal_holding_start": None}, "either a holding start"),
        ({"ordinary_holding_period_assumed_confirmed": False}, "Confirm ordinary"),
    ],
)
def test_conflicting_missing_or_unconfirmed_holding_facts_cannot_select_preferred_tax(
    changes, match
):
    data = dict(dated().model_dump(mode="json"), **changes)
    with pytest.raises(ValueError, match=match):
        PrivateFundContract.model_validate(data)


def test_legacy_character_is_preserved_but_dated_realization_cannot_precede_acquisition():
    assert (
        character(PrivateFundContract.model_validate(contract()), date(2026, 2, 1)) == "long_term"
    )
    with pytest.raises(ValueError, match="cannot precede"):
        character(dated(), date(2025, 12, 31))
