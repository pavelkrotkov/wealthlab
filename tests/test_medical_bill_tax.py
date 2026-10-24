"""Actual nonqualified provider amounts create tax, never another cash receipt."""

from medical_bill_cases import data

from wealthlab.household.projection import project
from wealthlab.household.scenario import Scenario


def test_nonqualified_provider_payment_uses_actual_funded_tax_adapter():
    value = data(
        amount=1000, hsa_amount=1000, eligibility="not_qualified", hsa_mode="allow_nonqualified"
    )
    plan = value["hsa_plan"]
    plan.update(
        nonqualified_treatment="ordinary_noninvestment_assumption",
        nj_withdrawal_taxable_fractions={"care": "0.5"},
        generated_distribution_tax_excluded_from_other_inputs_confirmed=True,
    )
    rows = project(Scenario.model_validate(value))
    first = rows[0]
    assert first["hsa_nonqualified_taxable"] == 1000
    assert first["hsa_additional_tax"] == 200
    assert first["hsa_nj_withdrawal_income"] == 500
    assert first["hsa_withdrawal_cash"] == 0
    assert sum(r["tax_event_cash"] for r in rows) == 0
    assert rows[-1]["net_wealth"] == 2800
    assert rows[11]["annual_tax"]["federal"]["agi"] == 1000
