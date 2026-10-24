"""An exit is conditional on liquid shares and its explicitly supplied forward-window assumption."""

import pytest
from test_harvest_comparison import harvest_case

from wealthlab.portfolio.cases import LotCase
from wealthlab.portfolio.engine import run


def test_unresolved_exit_window_is_not_silently_closed():
    payload = harvest_case()
    payload["end"] = "2026-06-15"
    payload["terminal_exit"]["no_replacements_next30_days"] = False
    result = run(LotCase.model_validate(payload))
    assert result["harvest_loss_summary"]["federal_pending_loss"] == 250
    assert result["harvest_comparison"]["holding"]["total_tax_saving"] == 0
    assert result["harvest_comparison"]["terminal_exit"]["total_tax_saving"] < 0
    payload["terminal_exit"]["no_replacements_next30_days"] = True
    confirmed = run(LotCase.model_validate(payload))
    assert confirmed["harvest_comparison"]["terminal_exit"]["total_tax_saving"] == 0


def test_locked_positions_remain_in_exit_result():
    payload = harvest_case()
    payload["lots"][0]["liquid_after"] = "2027-01-01"
    result = run(LotCase.model_validate(payload))
    assert result["terminal_exit"]["lots"][0]["id"] == "original"
    assert result["terminal_exit"]["closing_cash"] == 1000


def test_retirement_exit_is_not_misrepresented_as_spendable_cash():
    payload = harvest_case()
    payload["accounts"].append(dict(payload["accounts"][0], id="ira", wrapper="traditional_ira"))
    payload["terminal_exit"]["account_ids"] = ["ira"]
    with pytest.raises(ValueError, match="taxable accounts"):
        run(LotCase.model_validate(payload))
