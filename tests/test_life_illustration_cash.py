"""Independent dated cash, loan conservation and terminal-value examples."""

import pytest

from wealthlab.products.life_illustration import run
from wealthlab.products.life_illustration_example import flow, synthetic
from wealthlab.products.life_illustration_inputs import LifeStudy


def study(flows=None, **changes):
    data = synthetic().model_dump(mode="json")
    case = data["illustrations"][0]
    case.update(
        issue_date="2026-01-01",
        stop_funding_date=None,
        flows=flows or [flow("premium", "2026-01-01", "1000")],
        values=[
            dict(
                date="2027-01-01",
                gross_cash_value="1200",
                gross_surrender_value="1100",
                gross_death_benefit="5000",
            )
        ],
    )
    case.update(changes)
    data["illustrations"] = [case]
    return LifeStudy.model_validate(data)


def point(case):
    return run(case)["illustrations"][0]["rows"][-1]


def test_independent_living_surrender_and_death_returns():
    row = point(study())
    assert row["cash_value_irr"]["rate"] == pytest.approx(0.2)
    assert row["surrender_irr"]["rate"] == pytest.approx(0.1)
    assert row["death_irr"]["rate"] == pytest.approx(4)
    assert row["protection_shortfall"] == 1000
    assert row["loan_balance"] == 0


def test_loan_cash_has_equal_debt_and_non_cash_interest_reduces_exit_value():
    case = study(
        [
            flow("premium", "2026-01-01", "1000"),
            flow("advance", "2026-04-01", "400", "loan_advance"),
            flow("interest", "2026-07-01", "40", "capitalized_interest"),
            flow("repay", "2026-10-01", "100", "loan_principal_repayment"),
        ]
    )
    result = run(case)["illustrations"][0]
    row = result["rows"][0]
    assert row["loan_balance"] == 340
    assert row["net_surrender_value"] == 760
    assert row["net_death_benefit"] == 4660
    assert result["dated_cash"][2]["cash"] == 0
    # Repayment after the advance makes the cash-sign sequence nonconventional.
    assert row["surrender_irr"]["rate"] is None
    assert sum(item["cash"] for item in result["dated_cash"]) + row["net_surrender_value"] == 60


def test_separate_cash_dividend_and_external_fee_count_once():
    case = study(
        [
            flow("premium", "2026-01-01", "1000"),
            flow("fee", "2026-01-01", "100", "external_fee"),
            flow("dividend", "2027-01-01", "110", "dividend_cash"),
        ]
    )
    assert point(case)["surrender_irr"]["rate"] == pytest.approx(0.1)


def test_retirement_obligations_and_unknown_stop_funding_values_are_separate():
    result = run(synthetic())["illustrations"]
    assert result[0]["premiums_from_retirement"] == 1000
    assert result[3]["premiums_from_retirement"] == 2000
    assert result[4]["rows"][0]["net_death_benefit"] is None
    assert result[4]["rows"][0]["surrender_irr"]["rate"] is None
