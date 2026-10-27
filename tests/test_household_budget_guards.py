"""Forecast sources, dates, exclusions, rules and carry facts require explicit validation."""

import pytest

from tests.household_budget_cases import synthetic
from wealthlab.household.scenario import Scenario
from wealthlab.portfolio.household_book import Ledger


@pytest.mark.parametrize(
    "field,value",
    [
        ("source_reference", " "),
        ("source_date", "2026-02-01"),
        ("available_on", "2026-02-01"),
        ("provenance", "unresolved"),
        ("known_non_lot_facts_and_remaining_income_confirmed", False),
        ("excludes_all_modeled_lot_events_confirmed", False),
        ("fixed_forecast_deductions_confirmed", False),
    ],
)
def test_unavailable_or_unconfirmed_forecast_blocks_budget_result(field, value):
    data = synthetic().model_dump(mode="json")
    data["lot_plan"]["tax_budget_forecasts"][0][field] = value
    with pytest.raises(ValueError):
        Ledger(Scenario.model_validate(data))


@pytest.mark.parametrize(
    "path,value",
    [
        (("policy", "year"), 2025),
        (("policy", "annual_index"), 0.04),
        (("filing", "age_primary"), 41),
        (("nj_regime",), "published_2025"),
        (("federal_income", "short_carry"), "1"),
        (("federal_income", "long_carry"), "1"),
        (("payments", "federal_estimates"), "1"),
        (("nj_income", "retirement", "special_exclusion_eligible"), True),
    ],
)
def test_forecast_cannot_change_rule_person_eligibility_carry_or_cash_payment_facts(path, value):
    data = synthetic().model_dump(mode="json")
    target = data["lot_plan"]["tax_budget_forecasts"][0]["cases"][0]
    for key in path[:-1]:
        target = target[key]
    target[path[-1]] = value
    with pytest.raises(ValueError):
        Ledger(Scenario.model_validate(data))


def test_missing_forecast_or_actual_year_context_raises_clear_validation_error():
    data = synthetic().model_dump(mode="json")
    data["lot_plan"]["tax_budget_forecasts"] = []
    with pytest.raises(ValueError, match="explicit dated annual"):
        Ledger(Scenario.model_validate(data))
    data = synthetic().model_dump(mode="json")
    data["tax_plan"]["cases"][0]["policy"]["year"] = 2027
    with pytest.raises(ValueError, match="actual household tax context"):
        Ledger(Scenario.model_validate(data))


@pytest.mark.parametrize("duplicate", ["date", "id"])
def test_forecast_selection_is_not_ambiguous(duplicate):
    data = synthetic().model_dump(mode="json")
    first = data["lot_plan"]["tax_budget_forecasts"][0]
    other = dict(first, id="other", available_on="2026-02-01")
    if duplicate == "date":
        other["available_on"] = first["available_on"]
    else:
        other["id"] = first["id"]
    data["lot_plan"]["tax_budget_forecasts"].append(other)
    with pytest.raises(ValueError, match="ordered/unique"):
        Ledger(Scenario.model_validate(data))
