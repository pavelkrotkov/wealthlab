"""Tax ownership, pure auxiliary claims and saved source inputs retain distinct meanings."""

from decimal import Decimal

from wealthlab.household.projection import project
from wealthlab.household.storage import loads
from wealthlab.retirement.social_medicare_example import synthetic


def test_uninsured_pure_spouse_uses_its_auxiliary_record_for_premiums():
    case = synthetic()
    members = list(case.social_security.members)
    members[1] = members[1].model_copy(update=dict(own_insured=False, pia_january_2026=Decimal(0)))
    claims = case.social_security.model_copy(update=dict(members=members))
    rows = project(case.model_copy(update=dict(social_security=claims)))
    spouse = next(
        p for p in rows[-1]["medicare_audit"]["benefit_payments"] if p["member"] == "spouse"
    )
    assert spouse["active_record"] == "spousal_excess"
    assert spouse["cash_received"] == 1047
    assert spouse["gross_credited"] == Decimal("1249.90")


def test_preparation_and_projection_leave_saved_claims_and_income_sources_unchanged():
    case = synthetic()
    original = case.model_dump_json()
    rows = project(case)
    assert case.model_dump_json() == original
    assert [r.federal for r in case.tax_plan.income_rules] == ["interest"]
    assert project(loads(original)) == rows
