"""A broker-rejected physical delivery stays pending without fabricating shares or tax."""

from tests.option_cases import one_leg, parse
from wealthlab.products.option_engine import run


def test_locked_physical_shares_remain_owned_with_a_pending_delivery_failure():
    data = one_leg(side="short", physical=True)
    data["holdings"]["lots"][0]["liquid_after"] = "2027-01-01"
    result = run(parse(data))
    assert result["ending"]["shares"] == 100
    assert result["open_legs"] == ["contract"]
    assert result["failures"]
    assert result["tax"] == []
