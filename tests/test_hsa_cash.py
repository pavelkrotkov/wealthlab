"""Cash conservation includes employer funding and interest, never a fabricated tax refund."""

from wealthlab.retirement.hsa import run
from wealthlab.retirement.hsa_example import synthetic
from wealthlab.retirement.hsa_inputs import HSACase


def payload():
    return synthetic().model_dump(mode="json")


def calculate(data):
    return run(HSACase.model_validate(data))


def test_synthetic_cash_conserves_capital_and_funds_only_eligible_requests():
    """Employer funding adds capital; the personal transfer does not.

    Opening assets/cash total $17,000, plus $2,000 employer funding and $100
    interest. Reimbursements change where that $19,100 sits, never its total.
    """
    result = run(synthetic())
    assert result["cash"] == 4500
    assert result["account_balances"] == {"hsa": 10600, "spouse_hsa": 4000}
    assert result["cash"] + sum(result["account_balances"].values()) == 19100
    assert result["personal_federal_deduction"] == result["external_employer_funding"] == 2000
    assert result["new_jersey"] is None


def test_limit_block_and_cash_shortfall_are_distinct():
    result = calculate(payload())
    row = result["orders"][1]
    assert row["blocked_by_limit"] == 2437.50
    assert row["unfunded"] == 3562.50
    assert row["funded"] == 2000
    assert (row["owner"], row["account"]) == ("person", "hsa")
    assert result["contributions_funded"] == {"person": 4000, "spouse": 0}


def test_nj_cash_assumption_is_independent_of_federal_hsa_treatment():
    data = payload()
    data["nj_treatment"] = "taxable_bank_interest_assumption"
    result = calculate(data)
    assert result["new_jersey"]["personal_deduction"] == 0
    assert result["new_jersey"]["employer_contributions"] == 2000
    assert result["new_jersey"]["taxable_interest"] == 100
    assert result["cash"] == 4500
