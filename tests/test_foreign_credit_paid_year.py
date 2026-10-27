"""The paid-method credit year is neither the foreign liability year nor a cash forecast.

Historical source facts remain visible without entering current-year AGI.
A prior liability actually paid now uses the current-year source limit;
a prior payment does not create a current claim without its carry history.
"""

from copy import deepcopy
from decimal import Decimal

from wealthlab.tax.foreign_credit import evaluate
from wealthlab.tax.foreign_credit_example import synthetic
from wealthlab.tax.foreign_credit_inputs import ForeignCreditCase


def historical():
    data = synthetic().model_dump(mode="json")
    row = deepcopy(data["income"][1])
    row["id"] = "work_es_2024"
    row["value"]["date"] = "2024-06-30"
    data["income"].append(row)
    data["tax_cash"][0].update(liability_year=2024, income_ids=["work_es_2024"])
    return data


def test_prior_liability_paid_now_uses_actual_paid_year_without_redepositing_historical_income():
    result = evaluate(ForeignCreditCase.model_validate(historical()))
    cash = result["actual_tax_cash"][0]
    assert cash["liability_year"] == 2024
    assert cash["credit_year"] == 2025
    assert result["observed_tax_cash_outflow_usd"] == Decimal(11000)
    assert result["candidate"]["federal"]["agi"] == Decimal(100000)
    assert result["candidate"]["federal"]["foreign_tax_credit"] == Decimal("6724.50")


def test_prior_paid_year_is_not_automatically_shifted_into_current_credit_or_cash():
    data = historical()
    data["tax_cash"][0]["value"]["date"] = "2024-12-15"
    result = evaluate(ForeignCreditCase.model_validate(data))
    assert result["observed_tax_cash_outflow_usd"] == 0
    assert result["all_tax_history"][0]["credit_year"] == 2024
    assert result["candidate"]["federal"]["foreign_tax_credit"] == 0
    assert result["candidate"]["federal"]["agi"] == Decimal(100000)
