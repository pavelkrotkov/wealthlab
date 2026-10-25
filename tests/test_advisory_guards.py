"""Unknown terms, conditional coverage and unavailable valuation stages remain explicit."""

import pytest

from tests.advisory_cases import change, plain, with_fee
from wealthlab.household.projection import project


@pytest.mark.parametrize(
    "update, message",
    [
        (dict(provenance="unresolved"), "resolved nonempty source"),
        (dict(source_ref=" "), "resolved nonempty source"),
        (dict(contract_terms_and_valuation_basis_confirmed=False), "Confirm advisory terms"),
        (dict(outer_cash_fee_not_already_in_embedded_costs_confirmed=False), "separate outer"),
        (dict(source_date="2026-02-01"), "source and availability"),
        (dict(available_on="2026-02-01"), "source and availability"),
    ],
)
def test_fee_terms_must_be_sourced_and_available_before_accrual(update, message):
    case = with_fee(plain())
    with pytest.raises(ValueError, match=message):
        project(change(case, lambda p: p["schedules"][0].update(update)))


def test_conditional_absence_is_sourced_visible_and_not_a_typo_tolerant_default():
    case = with_fee(plain())

    def absent(plan):
        plan["schedules"][0]["covered"][0].update(account_id="future_option_book")

    with pytest.raises(ValueError, match="Required advisory valuation account"):
        project(change(case, absent))

    def conditional(plan):
        absent(plan)
        plan["schedules"][0]["covered"][0].update(presence="if_present")

    with pytest.raises(ValueError, match="source-confirmed absence"):
        project(change(case, conditional))

    def confirmed(plan):
        conditional(plan)
        plan["schedules"][0]["covered"][0].update(absence_permitted_by_source_confirmed=True)

    row = project(change(case, confirmed))[0]
    assert (
        row["advisory_fee_assessments"][0]["components"][0]["status"] == "source_confirmed_absent"
    )
    assert row["advisory_fees_assessed"] == row["advisory_fees_paid"] == 0


def test_restricted_cash_scope_and_duplicate_accounts_or_schedules_are_rejected():
    case = with_fee(plain())
    with pytest.raises(ValueError, match="ordered household cash pool"):
        project(change(case, lambda p: p.update(payment_account_ids=["brokerage"])))

    def repeated_account(plan):
        plan["schedules"][0]["covered"] *= 2

    with pytest.raises(ValueError, match="repeat an account"):
        project(change(case, repeated_account))
    with pytest.raises(ValueError, match="schedule IDs must be unique"):
        project(change(case, lambda p: p.update(schedules=p["schedules"] * 2)))
