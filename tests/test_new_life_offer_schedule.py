"""First funding, full closure and complete conditional failure/tax terms are native inputs."""

import pytest
from new_life_offer_cases import inputs, offer_changed

from wealthlab.optimization.new_life_offers import validate_offers


@pytest.mark.parametrize(
    "change", ["zero_premium", "receipt_first", "no_terminal", "late_terminal"]
)
def test_incomplete_premium_or_full_exit_paths_cannot_become_optional_offers(change):
    def edit(data):
        contract = data["holding"]["contract"]
        if change == "zero_premium":
            contract["events"][0]["amount"] = "0"
        if change == "receipt_first":
            contract["events"][0]["kind"] = "dividend_cash"
        if change == "no_terminal":
            contract["events"].pop()
        if change == "late_terminal":
            contract["events"][-1]["date"] = "2026-04-01"

    household, _ = inputs()
    with pytest.raises(ValueError, match=r"premium|terminal exit"):
        validate_offers(household, [offer_changed(edit)])


def test_supplied_coverage_before_first_actual_premium_is_rejected():
    household, _ = inputs()

    def edit(data):
        data["holding"]["contract"]["events"][0]["date"] = "2026-02-15"

    with pytest.raises(ValueError, match="zero before the first premium"):
        validate_offers(household, [offer_changed(edit)])


@pytest.mark.parametrize("change", ["missing_failure", "unknown_tax", "missing_value"])
def test_native_complete_calendar_failure_and_tax_validation_applies_to_every_offer(change):
    def edit(data):
        holding = data["holding"]
        if change == "missing_failure":
            holding["failure_exits"] = {}
        if change == "unknown_tax":
            holding["contract"]["federal_status"] = "unknown"
        if change == "missing_value":
            holding["contract"]["values"].pop(0)

    household, _ = inputs()
    with pytest.raises(ValueError, match=r"failure exit|eligibility|post-event policy value"):
        validate_offers(household, [offer_changed(edit)])
