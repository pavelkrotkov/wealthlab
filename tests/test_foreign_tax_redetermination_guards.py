"""Unknown amendment treatment preserves real refund cash and blocks a favorable conclusion."""

from decimal import Decimal

from foreign_redetermination_cases import synthetic_refund

from wealthlab.household.projection import project


def test_denied_or_unconfirmed_redetermination_does_not_forge_a_completed_prior_return():
    scenario = synthetic_refund()
    plan = scenario.foreign_tax_plan.model_copy(update=dict(prior_return_redetermination="denied"))
    observed = []
    rows = project(
        scenario.model_copy(update=dict(foreign_tax_plan=plan)), tax_observer=observed.append
    )
    june = {row["date"]: row for row in rows}["2027-06-01"]
    assert june["foreign_tax_refund_received"] == 7000
    assert june["foreign_redetermination_unresolved"]
    assert june["funding_failure"]
    assert not june["foreign_return_revisions"]
    assert observed[-1]["closed_returns"][2025].case.foreign_credits.regular == Decimal("6724.50")


def test_blocked_later_carry_year_cannot_partially_mutate_the_original_return():
    scenario = synthetic_refund()
    plan = scenario.foreign_tax_plan
    profiles = list(plan.credit_profiles)
    profiles[1] = profiles[1].model_copy(update=dict(eligibility="unresolved"))
    changed = scenario.model_copy(
        update=dict(foreign_tax_plan=plan.model_copy(update=dict(credit_profiles=profiles)))
    )
    observed = []
    rows = project(changed, tax_observer=observed.append)
    june = {row["date"]: row for row in rows}["2027-06-01"]
    assert june["foreign_tax_refund_received"] == 7000
    assert not june["foreign_return_revisions"]
    assert june["foreign_redetermination_unresolved"]
    assert observed[-1]["closed_returns"][2025].case.foreign_credits.regular == Decimal("6724.50")
    assert not rows[-1]["foreign_final_source_returns"]
