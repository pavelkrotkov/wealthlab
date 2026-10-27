"""Independent2025 bracket/foreign-share amounts and denied/unknown money outcomes."""

from decimal import Decimal

from wealthlab.tax.foreign_credit import evaluate
from wealthlab.tax.foreign_credit_example import synthetic
from wealthlab.tax.foreign_credit_inputs import ForeignCreditCase


def test_half_foreign_income_uses_its_own_limit_and_preserves_actual_foreign_cash():
    result = evaluate(synthetic())
    row = result["basket_audit"][0]
    assert row["net"] == Decimal(42125)
    assert row["limit"] == Decimal("6724.50")
    assert result["candidate"]["federal"]["income_tax"] == Decimal("6724.50")
    assert result["observed_tax_cash_outflow_usd"] == Decimal(11000)
    assert result["carry_audit"]["generated_excess"][0]["amount"] == Decimal("4275.50")
    assert result["carry_audit"]["prior_year_cash_refund_assumed"] == 0


def test_denial_preserves_economic_tax_cash_and_unknown_eligibility_blocks_credit():
    case = synthetic()
    denied = evaluate(case.model_copy(update=dict(eligibility="denied")))
    unknown = evaluate(case.model_copy(update=dict(eligibility="unresolved")))
    assert denied["candidate"]["federal"]["income_tax"] == Decimal(13449)
    assert unknown["candidate"] is None
    assert (
        denied["observed_tax_cash_outflow_usd"] == unknown["observed_tax_cash_outflow_usd"] == 11000
    )


def test_unused_general_limit_does_not_offset_passive_tax_or_move_between_people():
    data = synthetic().model_dump(mode="json")
    data["annual"]["federal_income"].update(wages_primary="50000", interest="50000")
    data["income"][0]["kind"] = "interest"
    data["income"][0]["basket"] = "passive"
    data["tax_cash"][0]["basket"] = "passive"
    data["passive_category_no_special_reclassification_confirmed"] = True
    data["tax_cash"][0]["income_ids"] = ["work_us"]
    # Foreign general wages cannot create passive-category source capacity.
    result = evaluate(ForeignCreditCase.model_validate(data))
    assert result["candidate"]["federal"]["foreign_tax_credit"] == 0
    assert result["carry_audit"]["generated_excess"][0]["basket"] == "passive"
    assert result["carry_audit"]["generated_excess"][0]["owner_id"] == "person_a"


def test_passive_source_credit_requires_independent_high_tax_classification_confirmation():
    data = synthetic().model_dump(mode="json")
    data["annual"]["federal_income"].update(wages_primary="50000", interest="50000")
    data["income"][1].update(kind="interest", basket="passive")
    data["tax_cash"][0]["basket"] = "passive"
    unknown = evaluate(ForeignCreditCase.model_validate(data))
    assert unknown["candidate"] is None
    assert unknown["observed_tax_cash_outflow_usd"] == Decimal(11000)
    data["passive_category_no_special_reclassification_confirmed"] = True
    result = evaluate(ForeignCreditCase.model_validate(data))
    assert result["basket_audit"][1]["claimed"] == Decimal("6724.50")
    assert result["basket_audit"][0]["claimed"] == 0
