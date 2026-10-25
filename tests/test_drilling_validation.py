"""Unknown eligibility, tax history, classifications and overlapping books cannot compute."""

import pytest
from drilling_cases import change, short

from wealthlab.household.projection import project


@pytest.mark.parametrize(
    "field,value",
    [
        ("legal_form", "unconfirmed"),
        ("federal_ordinary", "unconfirmed"),
        ("se_classification", "unconfirmed"),
        ("nj_exit_category", "unconfirmed"),
        ("reference_nj_wash_treatment", "unconfirmed"),
        ("working_interest_eligibility_supplied_confirmed", False),
        ("supplied_qbi_amt_history_and_limits_confirmed", False),
        ("paid_operating_costs_deductible_assumption_confirmed", False),
        ("all_cash_basis_terms_and_recognition_complete_confirmed", False),
        ("other_tax_inputs_exclude_product_confirmed", False),
        ("unmodeled_liability_risk_acknowledged", False),
        ("reference_zero_fees_and_no_external_identical_trades_confirmed", False),
    ],
)
def test_unconfirmed_source_contract_is_blocked(field, value):
    case = change(short(), lambda d: d["drilling_plan"].update({field: value}))
    with pytest.raises(ValueError):
        project(case)


@pytest.mark.parametrize(
    "field,value,message",
    [
        ("date", "2026-01-30", "complete household month"),
        ("provenance", "unresolved", "provenance"),
        ("supplemental_federal", {"wages_primary": "100"}, "supplements only"),
    ],
)
def test_invalid_month_or_duplicate_income_is_blocked(field, value, message):
    case = change(short(), lambda d: d["drilling_plan"]["observations"][0].update({field: value}))
    with pytest.raises(ValueError, match=message):
        project(case)


def test_zero_se_assumption_cannot_discard_supplied_earnings():
    def edit(data):
        data["drilling_plan"]["se_classification"] = "zero_under_supplied_classification"
        data["drilling_plan"]["observations"][0]["supplemental_federal"] = {
            "partnership_se_earnings_primary": "500"
        }

    with pytest.raises(ValueError, match="Zero-SE classification contradicts"):
        project(change(short(), edit))


def test_opening_household_account_and_product_value_must_reconcile():
    case = change(short(), lambda d: d["accounts"][1].update(balance="1"))
    with pytest.raises(ValueError, match="reconcile"):
        project(case)


def test_deferred_release_cannot_precede_the_funded_cost():
    def edit(data):
        data["drilling_plan"]["observations"][0]["deductions"][1]["federal_timing"] = dict(
            treatment="deferred", release_on="2026-01-01", eligibility_after_limits_assumed=True
        )

    with pytest.raises(ValueError, match="follow its funded source date"):
        project(change(short(), edit))


def test_ordinary_niit_exclusion_cannot_follow_from_gp_or_nonpassive_label():
    case = change(
        short(),
        lambda d: d["drilling_plan"].update(
            ordinary_nonsection1411_classification_supplied_confirmed=False
        ),
    )
    with pytest.raises(ValueError, match="independent ordinary-income NIIT"):
        project(case)
