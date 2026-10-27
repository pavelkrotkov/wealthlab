"""Carry vintages retain their owner/basket/year and do not create predicted cash."""

from decimal import Decimal

from wealthlab.tax.foreign_credit import evaluate
from wealthlab.tax.foreign_credit_example import synthetic
from wealthlab.tax.foreign_credit_inputs import ForeignCreditCase


def test_original_tenth_year_carry_uses_only_remaining_current_basket_capacity():
    data = synthetic().model_dump(mode="json")
    data["tax_cash"] = []
    data["opening_carries"] = [
        dict(
            id="old_general",
            owner_id="person_a",
            origin_year=2015,
            basket="general",
            available_usd="1000",
            source="Synthetic original unused2015 tax",
        )
    ]
    result = evaluate(ForeignCreditCase.model_validate(data))
    assert result["candidate"]["federal"]["foreign_tax_credit"] == Decimal(1000)
    assert result["carry_audit"]["opening"][0]["remaining"] == 0
    assert result["carry_audit"]["opening"][0]["origin_year"] == 2015
    assert result["observed_tax_cash_outflow_usd"] == 0


def test_expired_vintage_cannot_refresh_after_a_move_or_into_another_basket():
    data = synthetic().model_dump(mode="json")
    data["annual"]["policy"].update(year=2026, mode="freeze_2025")
    data["annual"]["nj_regime"] = "freeze_2025"
    data["as_of"] = "2026-12-31"
    for row in data["income"]:
        row["value"]["date"] = "2026-06-30"
    data["tax_cash"] = []
    data["passive_category_no_special_reclassification_confirmed"] = True
    data["opening_carries"] = [
        dict(
            id="expired",
            owner_id="person_a",
            origin_year=2015,
            basket="passive",
            available_usd="1000",
            source="Synthetic original unused2015 tax",
        )
    ]
    result = evaluate(ForeignCreditCase.model_validate(data))
    assert result["candidate"]["federal"]["foreign_tax_credit"] == 0
    assert result["carry_audit"]["opening"][0]["expired"] is True
    assert result["carry_audit"]["opening"][0]["origin_year"] == 2015


def test_unreviewed_prior_capacity_does_not_assume_a_cash_refund_or_final_forward_only_answer():
    case = synthetic().model_copy(
        update=dict(prior_year_carryback_capacity_reviewed_zero_confirmed=False)
    )
    result = evaluate(case)
    assert result["carry_audit"]["status"] == "prior_carryback_review_required"
    assert result["carry_audit"]["prior_year_cash_refund_assumed"] == 0
