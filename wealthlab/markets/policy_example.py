"""Illustrative policy schedules reuse actual marks; replacement eligibility is conditional."""

from wealthlab.household.scenario import Scenario
from wealthlab.markets.household_inputs import HouseholdBinding

CHOICES = ("Funding only", "Staged sales", "Concentration target", "Harvesting")


def enable(scenario, binding, choice):
    if choice == "Funding only":
        return scenario, binding
    data = scenario.model_dump(mode="json")
    linked = data["lot_plan"]
    case = linked["case"]
    if choice == "Harvesting":
        return harvesting(data, binding)
    schedule = [("2026-03-31", ".25"), ("2026-06-30", ".50"), ("2027-03-31", ".75")]
    mode = "original_fraction"
    if choice == "Concentration target":
        schedule, mode = [("2026-03-31", ".40"), ("2026-06-30", ".40")], "target_weight"
    case["sale_policies"] = [
        sale(index, when, fraction, mode, linked["opening_prices"])
        for index, (when, fraction) in enumerate(schedule)
    ]
    return Scenario.model_validate(data), binding


def sale(index, when, fraction, mode, prices):
    return dict(
        id=f"household_sale_{index}",
        provenance="illustration",
        date=when,
        account_id="brokerage",
        security_id="stock",
        mode=mode,
        fraction=fraction,
        prices=prices,
        commission="0",
        selection="hifo",
    )


def harvesting(data, binding):
    linked = data["lot_plan"]
    case = linked["case"]
    case["securities"].append(
        dict(
            id="replacement",
            provenance="illustration",
            kind="etf",
            wash_group="distinct_replacement_assumption",
            exposure_group="equity",
        )
    )
    linked["opening_prices"]["replacement"] = linked["opening_prices"]["stock"]
    case["closing_prices"]["replacement"] = case["closing_prices"]["stock"]
    for marks in linked["monthly_marks"]:
        marks["prices"]["replacement"] = marks["prices"]["stock"]
    case["harvest_policies"] = [
        dict(
            id="conditional_harvest",
            provenance="illustration",
            date="2026-01-31",
            account_id="brokerage",
            security_id="stock",
            replacement_id="replacement",
            replacement_eligible=True,
            prices=linked["opening_prices"],
            minimum_loss="1",
            minimum_loss_fraction=".01",
            commission_per_trade="0",
            selection="hifo",
        )
    ]
    plans = binding.model_dump(mode="json")
    plans["securities"].append(dict(plans["securities"][0], security_id="replacement"))
    return Scenario.model_validate(data), HouseholdBinding.model_validate(plans)
