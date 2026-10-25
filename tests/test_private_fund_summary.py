"""Receipts are flows; outstanding settlement claims use the latest balance of every fund."""

from types import SimpleNamespace

from wealthlab.ui import private_fund_household_results as ui


def test_multiple_fund_receipts_and_latest_claims_exclude_other_sleeve_cash(monkeypatch):
    observed = {}
    metric = SimpleNamespace(metric=lambda label, value: observed.update({label: value}))
    streamlit = SimpleNamespace(
        columns=lambda _: (metric, metric, metric),
        subheader=lambda _: None,
        caption=lambda _: None,
        json=lambda _: None,
    )
    monkeypatch.setattr(ui, "st", streamlit)

    def record(identity, cash, claim, complete):
        return dict(
            account_id=identity,
            redemption_paid=cash,
            fund_receivable=claim,
            fund_complete_liquidation=complete,
            fund_internal_equity=1,
        )

    rows = [
        dict(
            sleeve_audit=[
                record("a", 10, 100, False),
                record("b", 20, 50, False),
                record("a", 100, 0, True),
                dict(redemption_paid=1000),
            ]
        )
    ]
    ui.display_household(rows)
    assert observed["Actual product cash received"] == "$130.00"
    assert observed["Unsettled fund receivable"] == "$50.00"
    assert observed["Complete cash liquidation"] == "No"
