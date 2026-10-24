"""Program balance limits are shared, dated and independent of gift-tax thresholds."""

from tests.test_education_cash import calculate, payload


def test_program_limit_is_shared_across_owners_for_one_beneficiary():
    data = payload()
    data.update(opening_cash=30000, withdrawals=[], allocations=[], returns=[])
    data["plans"][0]["limits"] = [dict(effective="2025-01-01", maximum_balance=50000)]
    data["accounts"].append(
        {
            **data["accounts"][0],
            "id": "second",
            "owner": "student",
            "balance": 15000,
            "contribution_basis": 15000,
        }
    )
    result = calculate(data)
    assert result["orders"][0]["funded"] == 5000
    assert result["orders"][0]["blocked_by_limit"] == 10000
    assert result["orders"][0]["unfunded"] == 0


def test_later_limit_increase_is_not_visible_to_an_earlier_request():
    data = payload()
    data.update(opening_cash=40000, withdrawals=[], allocations=[], returns=[])
    data["accounts"][0].update(balance=300000, contribution_basis=300000)
    data["contributions"][0].update(amount=20000, date="2026-09-07")
    data["contributions"].append(
        {**data["contributions"][0], "id": "new_limit", "date": "2026-09-08"}
    )
    result = calculate(data)
    assert [row["funded"] for row in result["orders"]] == [5000, 20000]
    assert result["njbest_funded_contributions"] == 25000


def test_other_beneficiary_does_not_consume_program_room_for_the_student():
    data = payload()
    data.update(opening_cash=30000, withdrawals=[], allocations=[], returns=[])
    data["plans"][0]["limits"] = [dict(effective="2025-01-01", maximum_balance=50000)]
    data["accounts"].append(
        {**data["accounts"][0], "id": "other_student", "beneficiary": "parent", "balance": 50000}
    )
    result = calculate(data)
    assert result["orders"][0]["funded"] == 15000
