"""Independent statutory amounts and boundaries, separate from economic/cash calculations."""

from datetime import date
from decimal import Decimal
from types import SimpleNamespace

import pytest

from wealthlab.products.qoz_exit import exit_event
from wealthlab.products.qoz_tax import include, inclusion_date, opening

D = Decimal
PLAN = SimpleNamespace(
    federal="allowed", new_jersey="deferred", rural_30_percent_assumed_confirmed=False
)


def test_post_2026_step_precedes_five_year_inclusion_and_only_elected_growth_is_excluded():
    book = opening(
        D(100000), dict(federal=D(80000), new_jersey=D(60000)), date(2027, 1, 31), "short_term"
    )
    early = include(book, D(150000), date(2032, 1, 30), PLAN)
    assert early.federal.short_term == 0
    event = include(book, D(150000), date(2032, 1, 31), PLAN)
    assert event.federal.short_term == D(72000)
    assert event.new_jersey.dispositions == D(54000)
    assert event.cash_received == 0
    assert include(book, D(200000), date(2033, 1, 31), PLAN).federal.short_term == 0
    result = exit_event(book, D(200000), D(200000), date(2037, 1, 31), PLAN)
    # Federal qualifying 80% gets FMV basis; the other 20% still realizes $20k.
    assert result.federal.long_term == D(20000)
    assert result.new_jersey.dispositions == D(100000)


def test_legacy_and_new_regime_use_actual_investment_date_and_original_character():
    assert inclusion_date(date(2026, 12, 31)) == date(2026, 12, 31)
    assert inclusion_date(date(2027, 1, 31)) == date(2032, 1, 31)
    book = opening(
        D(100000), dict(federal=D(100000), new_jersey=D(100000)), date(2026, 1, 31), "long_term"
    )
    result = include(book, D(80000), date(2026, 12, 31), PLAN)
    assert result.federal.long_term == D(80000)
    assert result.cash_received == 0


@pytest.mark.parametrize("rural,expected", [(False, 90000), (True, 70000)])
def test_rural_confirmation_controls_only_the_five_year_basis_increment(rural, expected):
    plan = SimpleNamespace(rural_30_percent_assumed_confirmed=rural)
    book = opening(
        D(100000), dict(federal=D(100000), new_jersey=D(100000)), date(2027, 1, 31), "long_term"
    )
    result = include(book, D(120000), date(2032, 1, 31), plan)
    assert result.federal.long_term == D(expected)


def test_early_sale_includes_original_gain_and_retains_new_short_term_gain():
    book = opening(
        D(100000), dict(federal=D(100000), new_jersey=D(100000)), date(2027, 1, 31), "long_term"
    )
    result = include(book, D(120000), date(2027, 12, 31), PLAN, sale=True)
    assert result.federal.long_term == D(100000)
    sale = exit_event(book, D(120000), D(119000), date(2027, 12, 31), PLAN)
    assert sale.federal.short_term == D(19000)
    assert sale.cash_received == 0


def test_ten_year_stock_loss_retains_basis_without_claiming_an_fmv_election():
    book = opening(
        D(100000), dict(federal=D(100000), new_jersey=D(100000)), date(2027, 1, 31), "long_term"
    )
    include(book, D(120000), date(2032, 1, 31), PLAN)
    sale = exit_event(book, D(80000), D(79000), date(2037, 1, 31), PLAN)
    # Retain the $100k included-gain basis; $79k actual proceeds realizes a $21k loss.
    assert sale.federal.long_term == D(-21000)
    federal = next(r for r in book["log"] if r["event"] == "full_stock_sale")
    assert federal["basis"] == D(100000)
    assert federal["ten_year_election"] is False
