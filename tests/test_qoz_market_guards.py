"""Unobserved sources, unsupported subscriptions and ambiguous return conventions fail visibly."""

from dataclasses import replace

import pytest

from tests.qoz_market_cases import flat
from wealthlab.markets.household_run import run
from wealthlab.markets.qoz_validation import validate


@pytest.mark.parametrize(
    "changes, message",
    [
        (dict(account_id="other"), "complete native QOZ account"),
        (dict(factor="unknown"), "known asset factor"),
        (dict(return_source_description=" "), "nonempty return source"),
        (dict(net_entity_tax_pre_investor_cost_confirmed=False), "Confirm net entity"),
        (dict(replace_dated_asset_returns_confirmed=False), "replacement observations"),
    ],
)
def test_binding_terms_must_identify_the_complete_native_book_and_return_basis(changes, message):
    case, batch, binding = flat()
    selected = binding.qoz.model_copy(update=changes)
    with pytest.raises(ValueError, match=message):
        validate(case, batch, binding.model_copy(update=dict(qoz=selected)), 0)


def test_missing_plan_or_binding_and_separate_yield_are_not_silently_accepted():
    case, batch, binding = flat()
    with pytest.raises(ValueError, match="actual native QOZ plan"):
        validate(case.model_copy(update=dict(qoz_plan=None)), batch, binding, 0)
    with pytest.raises(ValueError, match="complete native QOZ account"):
        validate(case, batch, binding.model_copy(update=dict(qoz=None)), 0)
    yields = batch.cash_yields.copy()
    yields[0, 2, batch.assets.index("qof_assets")] = 0.01
    batch = replace(batch, cash_yields=yields)
    with pytest.raises(ValueError, match="zero separate cash yield"):
        validate(case, batch, binding, 0)


def test_missing_month_and_invalid_index_fail_before_any_execution():
    case, batch, binding = flat()
    with pytest.raises(ValueError, match="path index"):
        validate(case, batch, binding, 1)
    plan = case.qoz_plan.model_copy(update=dict(observations=case.qoz_plan.observations[:-1]))
    with pytest.raises(ValueError, match="ordered complete month-end"):
        validate(case.model_copy(update=dict(qoz_plan=plan)), batch, binding, 0)


def test_locked_subscription_and_blocked_source_need_real_native_adapters():
    case, batch, binding = flat(
        shocks=[dict(name="subscription lock", month=0, lock_months=dict(qof_assets=1))]
    )
    with pytest.raises(ValueError, match="pending-investment"):
        run(case, batch, binding)
    case, batch, binding = flat(
        shocks=[dict(name="source lock", month=0, lock_months=dict(source_stock=1))]
    )
    with pytest.raises(ValueError, match="exactly one already executed source disposal"):
        run(case, batch, binding)


def test_missing_source_policy_cannot_fabricate_a_disposal_or_eligible_gain():
    case, batch, binding = flat()
    linked = case.lot_plan.model_copy(
        update=dict(case=case.lot_plan.case.model_copy(update=dict(sale_policies=[])))
    )
    with pytest.raises(ValueError, match="exactly one already executed source disposal"):
        run(case.model_copy(update=dict(lot_plan=linked)), batch, binding)
