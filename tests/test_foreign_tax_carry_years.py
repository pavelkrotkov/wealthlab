"""Actual excess becomes one original vintage, never another monthly cash receipt.

The same work/source labels recur in2026, while their person/year identities
remain distinct. A $4,275.50 actual2025 excess uses2026's foreign-source room
once in its annual return. An unreviewed carryback disposition blocks that
future claim instead of silently treating all excess as forward-only.
"""

from decimal import Decimal

from foreign_tax_cases import multi_year

from wealthlab.household.projection import project
from wealthlab.household.scenario import Scenario


def test_actual_original_vintage_uses_next_year_capacity_without_repaying_foreign_tax():
    rows = project(Scenario.model_validate(multi_year()))
    last = rows[-1]
    carry = last["foreign_tax_credit"]["carry_audit"]["opening"][0]
    assert carry["origin_year"] == 2025
    assert carry["used"] == Decimal("4275.50")
    assert carry["remaining"] == 0
    assert last["annual_tax"]["federal"]["income_tax"] == Decimal("9173.50")
    assert last["foreign_tax_paid"] == 0
    assert not last["foreign_tax_unresolved"]


def test_recurring_labels_retain_person_and_recognition_year_in_auditable_native_tokens():
    row = project(Scenario.model_validate(multi_year()))[-1]
    identities = list(row["foreign_tax_source_identities"].values())
    assert len(identities) == 4
    assert {i["recognition_year"] for i in identities} == {2025, 2026}
    assert {i["source_id"] for i in identities} == {"work_us", "work_es"}
    assert {i["owner_id"] for i in identities} == {"person_a"}


def test_unknown_prior_carryback_capacity_cannot_generate_a_favorable_future_claim():
    data = multi_year()
    data["foreign_tax_plan"]["credit_profiles"][0][
        "prior_year_carryback_capacity_reviewed_zero_confirmed"
    ] = False
    row = project(Scenario.model_validate(data))[-1]
    assert row["annual_tax"]["federal"]["foreign_tax_credit"] == 0
    assert any("Prior-year" in reason for reason in row["foreign_tax_unresolved"])
    assert row["funding_failure"]
