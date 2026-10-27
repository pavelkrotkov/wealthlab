"""Computed Spain taxes and actual IP-paid SGF relief use the existing USD wallet once.

The initial outstanding solidarity tax is eliminated only after actual IP cash
is observed. The converged execution cannot pay both the old and revised bill.
"""

from decimal import Decimal

import pytest
from spain_execution_cases import single

from wealthlab.tax.jurisdiction_execution import evaluate


def test_actual_country_cash_recomputes_sgf_after_ip_is_paid_without_double_credit():
    scenario, spain = single()
    result = evaluate(scenario, spain=spain)
    final = result["rows"][-1]
    country = result["country_assessments"]["person_a_2025"]
    paid = country["result"]["recognized_payments_eur"]
    assert paid["wealth"] > 0
    assert paid["solidarity"] == 0
    assert country["outstanding_eur"] == dict(irpf=0, wealth=0, solidarity=0)
    total = sum(
        row["foreign_tax_paid"]
        + row["tax_settlement_paid"]
        + row["tax_withheld"]
        + row["tax_estimates_paid"]
        + row["prior_tax_paid"]
        for row in result["rows"]
    )
    assert final["closing_cash"] == Decimal(200000) - total
    assert not final["funding_failure"]
    assert len(result["reconciliation"]) >= 2


def test_no_sgf_cash_is_invented_when_actual_ip_already_eliminates_the_tax():
    scenario, spain = single()
    result = evaluate(scenario, spain=spain)
    records = [r for row in result["rows"] for r in row["foreign_tax_cash_records"]]
    assert len({r["id"] for r in records}) == 2
    assert {r["tax_type"] for r in records} == {"income", "wealth"}


def test_unknown_bilateral_credit_and_missing_source_identity_fail_closed():
    scenario, spain = single()
    with pytest.raises(ValueError, match="treaty credit allocation"):
        evaluate(
            scenario,
            spain=spain.model_copy(update=dict(spanish_foreign_credit_treatment="unresolved")),
        )
    with pytest.raises(ValueError, match="stable US person/year/source"):
        evaluate(scenario, spain=spain.model_copy(update=dict(source_links=[])))
