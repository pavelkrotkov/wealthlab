"""Malformed contractual terms cannot become plausible investment results."""

import pytest

from tests.option_cases import one_leg, parse
from wealthlab.products.option_engine import run


@pytest.mark.parametrize(
    "changes,message",
    [
        (dict(provenance="unresolved"), "Resolve option"),
        (dict(opened="2025-01-02"), "Every opening"),
        (dict(expiry="2025-01-01"), "Resolve option"),
        (dict(underlying="INDEX", settlement="physical"), "Physical index"),
        (dict(federal_class="section1256", settlement="physical"), "cash settlement"),
        (dict(side="short", federal_character="long_term"), "short-term"),
        (dict(rolls_to="missing"), "Roll target"),
    ],
)
def test_unsupported_option_terms_are_rejected(changes, message):
    data = one_leg()
    data["legs"][0].update(changes)
    with pytest.raises(ValueError, match=message):
        run(parse(data))


@pytest.mark.parametrize(
    "event,message",
    [
        (dict(leg_id="missing", date="2025-06-01", action="close", close_price="3"), "known leg"),
        (dict(leg_id="contract", date="2025-06-01", action="close"), "execution price"),
        (dict(leg_id="contract", date="2025-06-01", action="exercise"), "European"),
        (dict(leg_id="contract", date="2025-06-01", action="expire"), "contractual expiry"),
        (
            dict(leg_id="contract", date="2025-06-01", action="exercise", close_price="2"),
            "Only a closing",
        ),
    ],
)
def test_invalid_termination_is_rejected(event, message):
    data = one_leg()
    data["events"] = [event]
    with pytest.raises(ValueError, match=message):
        run(parse(data))
