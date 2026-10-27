"""Unresolved option/share wash history cannot become an allowed capital loss."""

import pytest

from tests.option_cases import one_leg, parse
from wealthlab.products.option_engine import run


def test_option_tax_cannot_silently_inherit_unsupported_nj_wash_tracking():
    data = one_leg()
    data["holdings"].update(nj_wash_treatment="federal_rules", opening_wash_context_complete=True)
    with pytest.raises(ValueError, match="option-specific"):
        run(parse(data))
