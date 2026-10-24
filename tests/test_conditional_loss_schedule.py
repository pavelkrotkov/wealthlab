"""Federal/state eligibility is independent; positive amounts and source data are preserved."""

from conditional_loss_cases import allocation

from wealthlab.products.conditional_allocations import events


def test_denied_losses_preserve_positive_income_and_never_generate_cash():
    item = allocation("denied", "denied")
    original = item.model_dump_json()
    result = events(item)
    assert len(result) == 1
    assert (result[0].federal.short_term, result[0].new_jersey.dispositions) == (50000, 50000)
    assert result[0].federal.long_term == result[0].new_jersey.business.partnership == 0
    assert result[0].cash_received == 0
    assert item.model_dump_json() == original


def test_deferred_federal_loss_does_not_move_positive_income_or_allowed_state_loss():
    result = events(allocation("deferred", "allowed"))
    assert [e.date.isoformat() for e in result] == ["2026-04-01", "2027-04-01", "2026-04-01"]
    assert result[1].federal.long_term == result[2].new_jersey.business.partnership == -12000
    assert result[1].federal.short_term == result[2].new_jersey.dispositions == 0
    assert sum(e.cash_received for e in result) == 0
