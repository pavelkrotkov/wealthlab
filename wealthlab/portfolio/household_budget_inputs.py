"""Dated full-year non-lot forecasts quote liability; they are never actual tax/cash events."""

from datetime import date

from pydantic import Field

from wealthlab.household.records import Record
from wealthlab.tax.annual import AnnualCase


class HouseholdBudgetForecast(Record):
    source_reference: str = Field(min_length=1, max_length=200)
    source_date: date
    available_on: date
    cases: list[AnnualCase] = Field(min_length=1)
    known_non_lot_facts_and_remaining_income_confirmed: bool
    excludes_all_modeled_lot_events_confirmed: bool
    fixed_forecast_deductions_confirmed: bool


def validate_order(forecasts, end):
    dates = [forecast.available_on for forecast in forecasts]
    identifiers = [forecast.id for forecast in forecasts]
    if dates != sorted(set(dates)) or len(identifiers) != len(set(identifiers)):
        raise ValueError("Budget forecast dates must be ordered/unique and IDs must be unique.")
    if any(day > end for day in dates):
        raise ValueError("Budget forecast availability must lie before the household horizon ends.")


def validate_source(forecast):
    confirmations = (
        forecast.known_non_lot_facts_and_remaining_income_confirmed,
        forecast.excludes_all_modeled_lot_events_confirmed,
        forecast.fixed_forecast_deductions_confirmed,
    )
    if not all(confirmations) or forecast.provenance == "unresolved":
        raise ValueError(
            "Confirm the dated non-lot forecast, complete exclusions and fixed deductions."
        )
    if not forecast.source_reference.strip() or forecast.source_date > forecast.available_on:
        raise ValueError(
            "Budget forecasts need a nonempty source available on/after its source date."
        )
