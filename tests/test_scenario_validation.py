"""Reject critical missing, non-finite, inconsistent or impossible inputs."""

import pytest
from pydantic import ValidationError

from wealthlab.household.projection import project
from wealthlab.household.scenario import Scenario


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("inflation", float("nan")),
        ("schema_version", 2),
        ("end", "2020-01-01"),
        ("usd_per_currency", {"USD": 2}),
        ("usd_per_currency", {"USD": float("inf")}),
        ("members", []),
        ("ytd", None),
    ],
)
def test_invalid_scenario(payload, field, value):
    payload[field] = value
    with pytest.raises(ValidationError):
        Scenario.model_validate(payload)


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("owner", "missing"),
        ("id", "salary"),
        ("balance", "NaN"),
        ("balance", "1.234"),
        ("balance", None),
        ("currency", "GBP"),
        ("monthly_fee", -1),
    ],
)
def test_invalid_account(payload, field, value):
    payload["accounts"][0][field] = value
    with pytest.raises(ValidationError):
        Scenario.model_validate(payload)


def test_unresolved_input_blocks_projection(payload):
    payload["accounts"][0]["provenance"] = "unresolved"
    with pytest.raises(ValueError, match="critical inputs"):
        project(Scenario.model_validate(payload))
