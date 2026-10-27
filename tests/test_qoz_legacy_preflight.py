"""Unsupported legacy elections fail before economic projection, including locked exits."""

from datetime import date
from types import SimpleNamespace

import pytest

from wealthlab.products.qoz_dates import validate_legacy_exit


@pytest.mark.parametrize(
    "requested,locked,treatment,rejected",
    [
        (2047, False, "allowed", False),
        (2047, True, "allowed", True),
        (2048, False, "allowed", True),
        (2048, False, "denied", False),
    ],
)
def test_legacy_preflight_uses_the_first_executable_sale(requested, locked, treatment, rejected):
    plan = SimpleNamespace(
        calls=[SimpleNamespace(date=date(2026, 1, 31))],
        federal=treatment,
        mode="fund",
        sale_requested=date(requested, 12, 31),
        sale_not_before=date(requested, 12, 31),
        observations=[
            SimpleNamespace(date=date(requested, 12, 31), locked=locked),
            SimpleNamespace(date=date(requested + 1, 1, 31), locked=False),
        ],
    )
    if rejected:
        with pytest.raises(ValueError, match="Legacy post-2047"):
            validate_legacy_exit(plan)
    else:
        validate_legacy_exit(plan)
