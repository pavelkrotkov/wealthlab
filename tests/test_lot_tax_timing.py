"""Cross-year wash adjustments stay with the loss year, never the replacement year."""

from test_lot_tax_reporting import forecast, reporting_case

from wealthlab.portfolio.cases import LotCase
from wealthlab.portfolio.engine import run


def test_january_replacement_revises_december_loss_recognition():
    payload = reporting_case(end="2027-12-31")
    payload["lot_tax_cases"].append(forecast(2027))
    payload["trades"][0]["date"] = "2026-12-20"
    payload["trades"][1]["date"] = "2027-01-10"
    first, second = run(LotCase.model_validate(payload))["annual_tax_comparison"]
    assert first["recognized_federal"]["long_term"] == 0
    assert first["recognized_nj"] == 0
    assert first["incremental_liability"] == second["incremental_liability"] == 0


def test_closing_before_forward_window_ends_does_not_spend_future_loss():
    payload = reporting_case()
    payload["trades"] = payload["trades"][:1]
    payload["trades"][0]["date"] = "2026-12-20"
    row = run(LotCase.model_validate(payload))["annual_tax_comparison"][0]
    assert row["pending_losses"] == {"federal": 250, "nj": 250}
    assert row["incremental_liability"] == 0


def test_retirement_account_sale_is_not_a_distribution():
    payload = reporting_case()
    payload["accounts"][0]["wrapper"] = "traditional_ira"
    payload["trades"] = payload["trades"][:1]
    payload["trades"][0]["price"] = "20"
    row = run(LotCase.model_validate(payload))["annual_tax_comparison"][0]
    assert row["recognized_federal"]["long_term"] == 0
    assert row["recognized_nj"] == 0
    assert row["incremental_liability"] == 0
