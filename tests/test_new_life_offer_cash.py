"""Selecting a whole policy path spends the existing household wallet without free capital."""

from new_life_offer_cases import inputs

from wealthlab.household.projection import project
from wealthlab.household.scenario import Scenario
from wealthlab.optimization.new_life_offers import apply, validate_offers


def test_no_selection_preserves_actual_cash_and_the_full_independent_protection_gap():
    household, offers = inputs()
    data = household.model_dump(mode="json")
    before = household.model_dump(mode="json")
    apply(data, offers, [])
    assert data == before
    rows = project(Scenario.model_validate(data))
    assert rows[-1]["closing_cash"] == 7000
    assert all(row["life_protection_shortfall"] == 150000 for row in rows)


def test_selected_offer_adds_only_zero_opening_capital_then_executes_real_premiums_and_exit():
    household, offers = inputs()
    data = household.model_dump(mode="json")
    validate_offers(household, offers)
    apply(data, offers, [offers[0].id])
    selected = Scenario.model_validate(data)
    assert sum(a.balance for a in selected.accounts) == 10000
    assert (
        data["life_plan"]["insurance_need_by_owner"]
        == household.model_dump(mode="json")["life_plan"]["insurance_need_by_owner"]
    )
    rows = project(selected)
    assert [r["closing_cash"] for r in rows] == [8000, 6000, 7100]
    assert rows[-1]["life_policy_audit"]["executed"][-1]["received_cash"] == 2100
    assert rows[-1]["annual_tax"]["federal"]["agi"] == 100
