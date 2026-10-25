"""Roll annotations cannot silently point back to or merge existing contracts."""

import pytest

from tests.option_cases import one_leg, parse
from wealthlab.products.option_engine import run


def test_self_roll_is_rejected_even_when_its_same_day_close_has_a_quote():
    data = one_leg()
    data["legs"][0]["rolls_to"] = "contract"
    data["events"] = [dict(leg_id="contract", date="2025-01-01", action="close", close_price="5")]
    with pytest.raises(ValueError, match="separate, acyclic"):
        run(parse(data))


def test_two_old_contracts_cannot_roll_into_one_target():
    data = one_leg()
    leg = data["legs"][0]
    leg["rolls_to"] = "new"
    data["legs"].extend(
        [dict(leg, id="second"), dict(leg, id="new", rolls_to=None, opened="2025-06-01")]
    )
    data["events"] = [
        dict(leg_id=name, date="2025-06-01", action="close", close_price="5")
        for name in ("contract", "second")
    ]
    with pytest.raises(ValueError, match="exactly one incoming"):
        run(parse(data))
