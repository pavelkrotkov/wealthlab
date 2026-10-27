"""Prepared-policy reuse matches a fresh native reference and never retains old credit arrays."""

from decimal import Decimal

from pr_execution_helpers import annual
from pr_prepared_reference import reference

from wealthlab.tax.foreign_credit_facts import ForeignCredits
from wealthlab.tax.pr_execution_context import prepare
from wealthlab.tax.pr_federal import calculate


def test_prepared_ratios_and_credit_changes_match_fresh_policy_and_reset_all_arrays():
    case, _ = prepare(annual())
    full, half = case.income, [case.income[0]]
    facts = ForeignCredits(regular=1000, eligibility="allowed", source="Synthetic supplied credit")
    for rows, credit in [(half, facts), (full, ForeignCredits()), (half, ForeignCredits())]:
        actual = calculate(case, rows, [], native_credits=credit)
        expected = reference(case, rows, credit)
        assert {key: actual[key] for key in expected} == expected
    assert calculate(case, half, [], native_credits=ForeignCredits())["standard_ratio"] == Decimal(
        ".5"
    )
