"""Unknown legal or state-source facts never become an automatic zero NJ bill."""

from decimal import Decimal

import pytest
from nj_residence_helpers import edited, state

from wealthlab.tax.annual import evaluate
from wealthlab.tax.nj_residence_example import row, synthetic


@pytest.mark.parametrize(
    "change, message",
    [
        (lambda p, _: p["people"][0].update(status="full_year"), "Declared NJ status"),
        (
            lambda p, _: p["people"][0].update(residency_facts_assumed_confirmed=False),
            "legal residence",
        ),
        (
            lambda p, _: p["people"][0].update(us_citizen_full_year_assumed_confirmed=False),
            "US citizen",
        ),
        (
            lambda p, _: p["people"][0]["periods"].append(
                dict(start="2025-06-01", end="2025-07-01")
            ),
            "overlap",
        ),
        (lambda p, _: p["people"][0]["periods"][0].update(end="2025-01-01"), "valid exclusive"),
        (lambda p, _: p["income"][1].update(nj_source="unresolved"), "sourcing is unresolved"),
        (lambda p, _: p["income"][1].update(owner_id="missing"), "existing owner"),
        (lambda p, _: p["income"][1].update(received="2024-06-30"), "recognition year"),
        (
            lambda p, _: p["income"][0].update(amount_and_classification_assumed_confirmed=False),
            "NJ income",
        ),
        (lambda p, _: p["income"][0].update(amount="-1"), "signed amounts"),
        (lambda p, _: p["income"].append(p["income"][0]), "IDs must be unique"),
        (lambda p, _: p.update(filing_election_assumed_confirmed=False), "filing election"),
        (lambda p, _: p.update(as_of="2026-01-01"), "observation date"),
        (lambda _, d: d["nj_income"].update(wages="99999"), "reconcile exactly"),
        (lambda _, d: d["nj_income"]["business"].update(business="10"), "business categories"),
        (lambda _, d: d["nj_deductions"].update(alimony="1000"), "dated, owner/return"),
    ],
)
def test_unknown_contradictory_or_unreconciled_facts_reject_instead_of_zero(change, message):
    with pytest.raises(ValueError, match=message):
        state(edited(change))


def test_pension_exclusion_is_not_inferred_from_full_year_core_eligibility():
    def change(profile, data):
        profile["income"].append(row("pension", "2025-10-31", 30000, "allowed", "pension"))
        profile["retirement_exclusions"] = "allowed"
        data["nj_income"]["pension"] = "30000"

    with pytest.raises(ValueError, match="explicitly denied"):
        state(edited(change))


def test_zero_worldwide_nonresident_denominator_with_positive_nj_gain_requires_supported_profile():
    def change(profile, data):
        profile["people"][0].update(status="nonresident", periods=[])
        profile["income"] = [
            row("nj", "2025-06-30", 10000, "allowed", "dispositions"),
            row("other", "2025-06-30", -10000, "denied", "dispositions"),
        ]
        data["nj_income"].update(wages="0", dispositions="0")

    with pytest.raises(ValueError, match="zero worldwide denominator"):
        state(edited(change))


def test_unallocated_and_overallocated_payments_cannot_offset_other_return_payable():
    case = synthetic()
    paid = case.payments.model_copy(update=dict(nj_estimates=1000))
    with pytest.raises(ValueError, match="per-return allocations"):
        evaluate(case.model_copy(update=dict(payments=paid)))
    profile = case.nj_residence.model_copy(
        update=dict(
            actual_payments_by_return={
                "nj:2025:person_a:nonresident": Decimal(1000),
            }
        )
    )
    with pytest.raises(ValueError, match="overpayments/refunds"):
        evaluate(case.model_copy(update=dict(payments=paid, nj_residence=profile)))
