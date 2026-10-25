"""Missing histories and a policy near loan exhaustion cannot become valid values."""

import pytest

from tests.test_life_illustration_cash import point, study
from wealthlab.products.life_illustration_example import flow
from wealthlab.products.life_illustration_inputs import LifeStudy


@pytest.mark.parametrize(
    "flag",
    ["complete_history_from_issue_confirmed", "values_match_cashflows_and_funding_path_confirmed"],
)
def test_unconfirmed_history_or_funding_match_makes_returns_unknown(flag):
    row = point(study(**{flag: False}))
    assert row["net_surrender_value"] is None
    assert row["surrender_irr"]["rate"] is None


@pytest.mark.parametrize("cash_value", ["400", None])
def test_debt_at_cash_value_or_missing_collateral_needs_actual_contract_terms(cash_value):
    data = study(
        [flow("premium", "2026-01-01", "1000"), flow("loan", "2026-06-01", "400", "loan_advance")]
    ).model_dump(mode="json")
    data["illustrations"][0]["values"][0]["gross_cash_value"] = cash_value
    row = point(LifeStudy.model_validate(data))
    assert row["loan_balance"] == 400
    assert row["loan_contract_review_required"] is True
    assert row["net_death_benefit"] is None
    assert row["death_irr"]["rate"] is None
    for key in ("cash_value_irr", "surrender_irr", "death_irr"):
        assert (
            row[key]["status"] == "contract review required: loan collateral unknown or exhausted"
        )


@pytest.mark.parametrize(
    "change,message",
    [
        ({"stop_funding_date": "2025-12-31"}, "cannot precede"),
        ({"provenance": "unresolved"}, "Resolve critical"),
        ({"issue_date": "2027-01-01"}, "issue-to-last-value"),
    ],
)
def test_critical_contract_boundaries_reject(change, message):
    with pytest.raises(ValueError, match=message):
        study(**change)


def test_stop_funding_is_a_supplied_path_not_a_premium_deletion_rule():
    with pytest.raises(ValueError, match="later premiums"):
        study(
            [flow("first", "2026-01-01", "1000"), flow("later", "2026-02-01", "1000")],
            stop_funding_date="2026-01-01",
        )


def test_repayment_cannot_create_negative_debt():
    with pytest.raises(ValueError, match="exceed"):
        study([flow("repay", "2026-01-01", "1", "loan_principal_repayment")])
