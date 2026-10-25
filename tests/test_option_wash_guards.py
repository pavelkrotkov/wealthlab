"""Unresolved option/share wash history cannot become an allowed capital loss."""

import pytest

from tests.option_cases import one_leg, parse
from wealthlab.products.option_engine import run


def test_option_tax_cannot_silently_inherit_unsupported_nj_wash_tracking():
    data = one_leg()
    data["holdings"].update(nj_wash_treatment="federal_rules", opening_wash_context_complete=True)
    with pytest.raises(ValueError, match="option-specific"):
        run(parse(data))


def test_unresolved_option_share_wash_history_blocks_conditional_loss_recognition():
    data = one_leg()
    data["marks"][-1]["stock"] = "80"
    data["tax"]["wash_sales"] = "unresolved"
    result = run(parse(data))
    assert all(row["recognized"] is None for row in result["tax"])
    assert result["ending"]["cash"] == 9500
