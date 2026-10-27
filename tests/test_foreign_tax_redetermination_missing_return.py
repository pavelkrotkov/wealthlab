"""A supplied opening carry cannot substitute for the actual original US return.

The later run knows actual historical foreign payment and source facts. It can
receive the linked refund, but cannot fabricate US2025 liability/payment facts
from an opening credit-vintage amount when only US2026/2027 returns exist.
"""

from wealthlab.household.projection import project
from wealthlab.household.scenario import Scenario
from wealthlab.tax.foreign_credit_example import synthetic
from wealthlab.tax.foreign_redetermination_example import synthetic_refund


def missing_original():
    data = synthetic_refund().model_dump(mode="json")
    data["start"] = "2026-10-01"
    plan, foreign = data["tax_plan"], data["foreign_tax_plan"]
    first = plan["cases"][1]
    first["federal_income"]["wages_primary"] = "100000"
    first["nj_income"]["wages"] = "100000"
    first["payments"]["employee_payroll_withheld"] = "7650"
    plan["cases"] = [first, plan["cases"][2]]
    plan["events"] = [plan["events"][1]]
    historical = foreign["credit_profiles"][0]["income"]
    profiles = foreign["credit_profiles"][1:]
    profiles[0].update(
        annual=first,
        opening_carries=[
            dict(
                id="known_vintage",
                owner_id="person_a",
                origin_year=2025,
                basket="general",
                available_usd="4275.50",
                source="Supplied carry; original return unavailable",
            )
        ],
    )
    profiles[0]["income"].extend(historical)
    foreign["credit_profiles"] = profiles
    record = synthetic().tax_cash[0].model_dump(mode="json")
    record.update(id="es_installment_2025_10_31")
    record["value"]["date"] = "2025-10-31"
    foreign.update(
        schedules=[],
        opening_payments=[
            dict(assessment_id="es_income_2025", source_income_year=2025, record=record)
        ],
    )
    return Scenario.model_validate(data)


def test_missing_actual_original_return_blocks_reconciliation_without_erasing_real_refund():
    rows = project(missing_original())
    june = {row["date"]: row for row in rows}["2027-06-01"]
    assert june["foreign_tax_refund_received"] == 7000
    assert "actual original paid-year US return" in june["foreign_redetermination_unresolved"][0]
    assert june["funding_failure"]
    assert not june["foreign_return_revisions"]
    assert not rows[-1]["foreign_final_source_returns"]
