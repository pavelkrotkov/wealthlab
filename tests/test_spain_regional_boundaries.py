"""Independent printed 2025 AEAT quota boundaries, including late-2025 revised schedules."""

from decimal import Decimal

import pytest

from wealthlab.tax.spain import evaluate
from wealthlab.tax.spain_example import income, synthetic
from wealthlab.tax.spain_inputs import SpainCase


@pytest.mark.parametrize(
    ("region", "base", "printed_quota"),
    [
        ("andalusia", "21100", "2207"),
        ("aragon", "52500", "7455.79"),
        ("asturias", "17707.20", "1751.36"),
        ("balearic", "48000", "6660"),
        ("canarias", "19422", "1889.83"),
        ("cantabria", "35200", "4044"),
        ("castilla_leon", "53407.20", "7518.83"),
        ("extremadura", "24200", "2411"),
        ("galicia", "35200", "4215.96"),
        ("murcia", "34000", "3886.15"),
        ("la_rioja", "40000", "4711.90"),
        ("valencia", "72000", "12280"),
    ],
)
def test_regional_quota_at_independently_published_floor(region, base, printed_quota):
    data = synthetic(region).model_dump(mode="json")
    data.update(
        incomes=[income("general", base, "general")],
        general_reduction_eur="0",
        long_held_gain_cap_exclusion_eur="0",
    )
    data["regional_minimum_eur"] = "0"
    assessment = evaluate(SpainCase.model_validate(data))["income"]["assessment"]
    assert assessment["regional"]["general"] == Decimal(printed_quota)
