"""Dated cash conservation and independently computed annual basis ratios."""

from decimal import Decimal

from wealthlab.retirement.distribution_example import synthetic
from wealthlab.retirement.distribution_inputs import DistributionCase
from wealthlab.retirement.distributions import run


def payload():
    data = synthetic().model_dump(mode="json")
    data["annual_tax_case"] = None
    return data


def calculate(data):
    return run(DistributionCase.model_validate(data))


def test_cash_transfer_basis_and_recapture_are_separate():
    result = calculate(payload())
    assert result["cash"] == 35000
    assert result["account_balances"] == {"ira": 70000, "roth": 45000}
    assert result["cash"] + sum(result["account_balances"].values()) == 150000


def test_federal_pro_rata_includes_unwithdrawn_ira_accounts():
    data = payload()
    data["accounts"].append(dict(data["accounts"][0], id="other_ira", balance="50000.00"))
    result = calculate(data)
    rows = result["orders"][:2]
    assert [row["federal_basis_recovered"] for row in rows] == [
        Decimal("1333.33"),
        Decimal("2666.67"),
    ]
    assert result["owners"][0]["federal_ira_basis"] == 16000
    assert sum(row["nj_basis_recovered"] for row in rows) == 10000


def test_federal_nj_recognition_and_early_tax_have_distinct_amounts():
    rows = calculate(payload())["orders"]
    actual = [(r["federal_taxable"], r["nj_taxable"], r["additional_tax"]) for r in rows]
    assert actual == [(8000, 5000, 800), (16000, 10000, 0), (0, Decimal("7142.86"), 1500)]
