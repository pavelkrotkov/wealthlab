"""Independent cash identities, retirement cutoffs and real-dollar reporting."""

from decimal import Decimal

from wealthlab.household.projection import project
from wealthlab.household.scenario import Scenario


def test_no_return_conservation_and_retirement(payload):
    rows = project(Scenario.model_validate(payload))
    assert len(rows) == 24
    assert rows[11]["closing_cash"] == 172_000
    assert rows[-1]["closing_cash"] == 124_000
    assert rows[-1]["net_wealth"] == 224_000
    assert rows[12]["income"] == 0
    assert rows[-1]["reserve_target"] == 96_000


def test_every_month_reconciles(payload):
    rows = project(Scenario.model_validate(payload))
    for row in rows:
        spending = sum(
            row[key]
            for key in ("essential", "healthcare", "mortgage", "education", "discretionary")
        )
        outflow = spending + row["debt_payment"] + row["fees"] + row["contributions"]
        assert row["closing_cash"] == row["opening_cash"] + row["income"] - outflow
    assert rows[-1]["real_net_wealth"] < rows[-1]["net_wealth"]


def test_partial_month_and_ytd_not_double_counted(payload):
    payload.update(start="2026-01-16", end="2026-02-01")
    payload["ytd"].update(gross_income=50_000, federal_tax_paid=8_000)
    payload["members"][0]["retirement_date"] = "2026-01-24"
    row = project(Scenario.model_validate(payload))[0]
    assert row["income"] == Decimal("2580.65")  # Eight days of a 31-day month.
    assert row["essential"] == Decimal("2064.52")  # Sixteen days.
    assert row["closing_cash"] == Decimal("100516.13")
