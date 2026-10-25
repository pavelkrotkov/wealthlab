"""Pending losses earn no early benefit; paired forecast carries remain separate across years."""

from tests.household_budget_cases import two_year
from wealthlab.household.projection import project
from wealthlab.household.scenario import Scenario


def test_observed_loss_uses_paired_forecast_carries_without_creating_actual_refund_cash():
    rows = project(loss_case())
    decisions = rows[-1]["lot_audit"]["sale_decisions"]
    audits = rows[-1]["lot_audit"]["budget_audit"]
    # The $5k January loss is still pending on its decision date. Once mature,
    # $3k offsets forecast wages at22%, leaving $2k federal-only carry. Against
    # next year's external $5k gain, that carry saves $300 at15%, not twice.
    assert decisions[0]["sold_units"] == 100
    assert decisions[0]["estimated_incremental_liability"] == 0
    assert audits[0]["estimate_after_observed_trades"] == -660
    assert decisions[1]["estimated_incremental_liability"] == -300
    assert rows[-1]["closing_cash"] == 11000
    assert sum(row["tax_refund_received"] for row in rows) == 0


def test_later_carry_cannot_be_supplied_and_computed_a_second_time():
    import pytest

    from wealthlab.portfolio.household_book import Ledger

    data = two_year().model_dump(mode="json")
    data["lot_plan"]["tax_budget_forecasts"][0]["cases"][1]["federal_income"]["long_carry"] = "1"
    with pytest.raises(ValueError, match="only in the first year"):
        Ledger(Scenario.model_validate(data))


def loss_case():
    data = two_year().model_dump(mode="json")
    book = data["lot_plan"]["case"]
    book["lots"][0].update(federal_basis="15000", nj_basis="15000")
    book["sale_policies"] = [
        policy for policy in book["sale_policies"] if policy["date"].endswith("01-31")
    ]
    for policy in book["sale_policies"]:
        policy["tax_budget"] = "0"
    future = data["lot_plan"]["tax_budget_forecasts"][0]["cases"][1]
    future["federal_income"]["long_term"] = "5000"
    future["nj_income"]["dispositions"] = "5000"
    return Scenario.model_validate(data)
