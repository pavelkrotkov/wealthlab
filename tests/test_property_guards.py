"""Incomplete title, source, timing, lien or tax facts cannot silently create sale proceeds."""

import pytest

from wealthlab.household.projection import project
from wealthlab.household.property_example import synthetic
from wealthlab.household.scenario import Scenario

HOME = ("property_plan", "holdings", 0)
SALE = (*HOME, "sale")
MARK = (*HOME, "observations", 0)


INVALID_CASES = [
    (("tax_plan",), None, "explicit independent household tax"),
    (("start",), "2026-01-02", "complete calendar months"),
    (("accounts", 1, "currency"), "EUR", "USD property account"),
    (("debts", 0, "currency"), "EUR", "existing USD household"),
    (
        ("property_plan", "other_tax_inputs_exclude_property_recognition_confirmed"),
        False,
        "excluded duplicate",
    ),
    (
        ("property_plan", "debt_payoff_full_month_native_interest_confirmed"),
        False,
        "native full-month",
    ),
    ((*HOME, "account_id"), "cash", "Bind every native property"),
    ((*HOME, "provenance"), "unresolved", "resolved source"),
    ((*HOME, "source_ref"), "  ", "resolved source"),
    ((*HOME, "available_on"), "2026-02-01", "projection opening"),
    ((*HOME, "use"), "rental_or_business", "rental"),
    ((*HOME, "ownership_legal_use_and_tax_facts_supplied_confirmed"), False, "legal/use"),
    (
        (*HOME, "unchanged_basis_and_no_other_asset_cashflows_confirmed"),
        False,
        "changing-basis",
    ),
    ((*HOME, "linked_debt_ids"), ["missing_lien"], "existing USD household"),
    ((*HOME, "linked_debt_ids"), ["home_lien", "home_lien"], "linked debt"),
    ((*HOME, "observations", 1, "id"), "home_mark_0", "source record"),
    ((*MARK, "date"), "2026-02-01", "every modeled month"),
    ((*MARK, "available_on"), "2026-02-01", "own cutoff"),
    ((*MARK, "provenance"), "unresolved", "own cutoff"),
    ((*HOME, "terminal_action"), "retain", "explicit retained"),
    ((*HOME, "sale"), None, "complete dated sale"),
    ((*SALE, "date"), "2026-06-15", "month-end closing"),
    ((*SALE, "provenance"), "unresolved", "resolved observed"),
    ((*SALE, "federal_character"), "unconfirmed", "independent property tax"),
    ((*SALE, "costs_due_only_on_executed_close_confirmed"), False, "closing costs"),
    ((*SALE, "no_closing_withholding_or_other_escrow_terms_confirmed"), False, "withholding"),
    (
        (*SALE, "prelimited_tax_recognition_and_no_deduction_claims_confirmed"),
        False,
        "independent property tax",
    ),
    ((*SALE, "federal_taxable_gain"), "50000", "independent net economic gains"),
    ((*SALE, "nj_taxable_gain"), "60000", "independent net economic gains"),
    (("accounts", 1, "monthly_fee"), "1", "zero generic fee"),
    (("accounts", 1, "wrapper"), "taxable", "Bind every native property"),
    (
        ("tax_plan", "cases", 0, "federal_deductions", "qualified_mortgage_interest"),
        "100",
        "dated attribution",
    ),
]


@pytest.mark.parametrize("path,value,message", INVALID_CASES)
def test_incomplete_property_profiles_are_rejected(path, value, message):
    data = synthetic().model_dump(mode="json")
    item = data
    for key in path[:-1]:
        item = item[key]
    item[path[-1]] = value
    with pytest.raises(ValueError, match=message):
        project(Scenario.model_validate(data))
